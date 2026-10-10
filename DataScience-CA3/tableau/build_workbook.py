"""Generate the Tableau workbook (Enron_Email_Network.twb + packaged .twbx) from data/processed/*.csv.

Usage : python3 tableau/build_workbook.py
Output: tableau/Enron_Email_Network.twb, tableau/Data/enron/*.csv (unpackaged, opens in place)
        tableau/Enron_Email_Network.twbx                          (packaged: workbook + data in one file)

Format: the classic version-18.1 workbook dialect exactly as Tableau 2021.x saved it (explicit feature manifest,
_.fcp.* dual elements for the object model), mirrored element by element from genuine Tableau-saved workbooks.
Tableau Desktop / Public of any later version (incl. 2026.x) upgrades it on open. The newer "26.1 +
<ManifestByVersion/>" dialect was tried first and is rejected by Tableau 2026.2.3's loader, so it is not used.

Interactivity deliberately avoids constructs that changed between versions: dashboard filtering is driven by
parameters (+ a "Keep/Drop" calculated filter on each sheet) instead of shared filter groups, and the Top-15 chart
is ordered by a rank label instead of a sort element.
"""
import hashlib
import re
import shutil
import uuid
import zipfile
from pathlib import Path

import pandas as pd
from lxml import etree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = ROOT / "data" / "processed"
DATA_DIR = "Data/enron"
NAME = "Enron_Email_Network"
VERSION = "18.1"
SOURCE_BUILD = "2021.3.3 (20213.21.1018.0949)"
USER = "http://www.tableausoftware.com/xml/user"
U = "{%s}" % USER
OM_T = "_.fcp.ObjectModelEncapsulateLegacy.true..."      # feature-prefixed names as Tableau 2021 writes them
OM_F = "_.fcp.ObjectModelEncapsulateLegacy.false..."
TT_T = "_.fcp.ObjectModelTableType.true..."
SV_F = "_.fcp.SchemaViewerObjectModel.false..."

# ----------------------------------------------------------------------------------------------- palette
COMMUNITY_COLOURS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
PERIOD_COLOURS = {"1 Pre-crisis": "#2a78d6", "2 Crisis (Aug-Dec 2001)": "#eb6834", "3 Post-bankruptcy": "#8a909c"}
ROLE_COLOURS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#b9bec8"]
TIE_COLOURS = {"Strong (two-way)": "#8f96a3", "Weak (one-way)": "#d5d9e0", "None": "#ffffff"}
METRIC_COLOURS = {"Observed: P(friend-of-friend tie)": "#2a78d6", "Expected at random: edge density": "#eb6834"}
INK, MUTED = "#111418", "#4a5160"


def stable_id(text, n=28, alphabet="0123456789abcdefghijklmnopqrstuvwxyz"):
    h = int(hashlib.sha256(text.encode()).hexdigest(), 16)
    out = ""
    for _ in range(n):
        h, r = divmod(h, len(alphabet))
        out += alphabet[r]
    return out


def guid(text):
    return "{" + str(uuid.UUID(hashlib.md5(text.encode()).hexdigest())).upper() + "}"


def q(s):
    """Tableau writes string literals inside attribute values with surrounding double quotes."""
    return f'"{s}"'


def csv_values(file, col):
    return sorted(pd.read_csv(SRC / file)[col].dropna().unique())


# ----------------------------------------------------------------------------------------------- parameters
ALL_PERIODS, ALL_ROLES, ALL_COMMS = "All periods", "All roles", "All communities"
PARAMS = {  # name -> (caption, default, members)
    "Parameter 1": ("Rank people by", "Betweenness", ["Betweenness", "PageRank", "Contacts", "Emails sent"]),
    "Parameter 2": ("Period", ALL_PERIODS, [ALL_PERIODS] + csv_values("deliveries.csv", "period")),
    "Parameter 3": ("Sender role", ALL_ROLES, [ALL_ROLES] + csv_values("deliveries.csv", "sender_role")),
    "Parameter 4": ("Ties shown", "Strong ties only", ["Strong ties only", "All ties"]),
    "Parameter 5": ("Community", ALL_COMMS,
                    [ALL_COMMS] + sorted(csv_values("employees.csv", "community"), key=lambda c: int(c.split()[0][1:]))),
}


# ----------------------------------------------------------------------------------------------- data model
class Col:
    def __init__(self, name, datatype, role, type_, caption=None, fmt=None):
        self.name, self.datatype, self.role, self.type, self.caption, self.fmt = name, datatype, role, type_, caption, fmt


class Calc(Col):
    def __init__(self, cid, caption, datatype, role, type_, formula, fmt=None):
        super().__init__(cid, datatype, role, type_, caption, fmt)
        self.formula = formula


def dim(name, caption, datatype="string", type_="nominal"):
    return Col(name, datatype, "dimension", type_, caption)


def mea(name, caption, datatype="real", fmt=None):
    return Col(name, datatype, "measure", "quantitative", caption, fmt)


def keep(cid, caption, condition):
    return Calc(cid, caption, "string", "dimension", "nominal", f'IF {condition} THEN "Keep" ELSE "Drop" END')


DS = {
    "deliveries": dict(caption="Email deliveries", file="deliveries.csv", cols=[
        dim("delivery_id", "Delivery ID", "integer", "ordinal"),
        dim("message_id", "Message ID", "integer", "ordinal"),
        dim("sent_at", "Sent at", "datetime", "ordinal"),
        dim("sender", "Sender"), dim("sender_role", "Sender role"), dim("sender_community", "Sender community"),
        dim("recipient", "Recipient"), dim("recipient_role", "Recipient role"),
        dim("recipient_community", "Recipient community"), dim("recipient_type", "Recipient type"),
        mea("n_recipients", "Recipients in message", "integer"),
        dim("period", "Period"), dim("direction", "Direction (by seniority)"), dim("community_link", "Community link"),
    ], calcs=[
        Calc("Calculation_1000000000000000001", "Deliveries", "integer", "measure", "quantitative", "1", "n#,##0"),
        Calc("Calculation_1000000000000000002", "Cross-community share", "real", "measure", "quantitative",
             'SUM(IF [community_link] = "Across communities" THEN 1 ELSE 0 END) / '
             "SUM([Calculation_1000000000000000001])", "p0.0%"),
        keep("Calculation_1000000000000000003", "Keep row (period, role)",
             f'([Parameters].[Parameter 2] = "{ALL_PERIODS}" OR [period] = [Parameters].[Parameter 2]) AND '
             f'([Parameters].[Parameter 3] = "{ALL_ROLES}" OR [sender_role] = [Parameters].[Parameter 3])'),
    ]),
    "employees": dict(caption="People (network metrics)", file="employees.csv", cols=[
        dim("employee_key", "Pseudonym key"), dim("display_name", "Person"), dim("named_officer", "Named officer"),
        dim("role_group", "Role group"), dim("role_rank", "Role rank", "integer", "ordinal"),
        dim("community", "Community"), dim("community_louvain", "Louvain community"),
        mea("emails_sent", "Emails sent", "integer"), mea("emails_received", "Emails received", "integer"),
        mea("out_contacts", "Out-contacts", "integer"), mea("in_contacts", "In-contacts", "integer"),
        mea("contacts", "Contacts (degree)", "integer"), mea("strong_ties", "Strong ties", "integer"),
        mea("weak_ties", "Weak ties", "integer"), mea("betweenness", "Betweenness centrality"),
        mea("pagerank", "PageRank"), mea("clustering", "Clustering coefficient"),
        mea("crisis_share", "Share of own email sent in crisis", fmt="p0%"),
        mea("x", "x"), mea("y", "y"),
        mea("rank_betweenness", "Rank: betweenness", "integer"), mea("rank_pagerank", "Rank: PageRank", "integer"),
        mea("rank_contacts", "Rank: contacts", "integer"), mea("rank_emails_sent", "Rank: emails sent", "integer"),
    ], calcs=[
        Calc("Calculation_2000000000000000001", "Selected metric", "real", "measure", "quantitative",
             'CASE [Parameters].[Parameter 1] WHEN "Betweenness" THEN [betweenness] WHEN "PageRank" THEN [pagerank] '
             'WHEN "Contacts" THEN [contacts] WHEN "Emails sent" THEN [emails_sent] END'),
        Calc("Calculation_2000000000000000002", "Selected rank", "integer", "measure", "quantitative",
             'CASE [Parameters].[Parameter 1] WHEN "Betweenness" THEN [rank_betweenness] '
             'WHEN "PageRank" THEN [rank_pagerank] WHEN "Contacts" THEN [rank_contacts] '
             'WHEN "Emails sent" THEN [rank_emails_sent] END'),
        Calc("Calculation_2000000000000000003", "Rank", "string", "dimension", "nominal",
             'RIGHT("0" + STR([Calculation_2000000000000000002]), 2) + ". " + [display_name]'),
    ]),
    "network": dict(caption="Network paths (node-link layout)", file="network_paths.csv", cols=[
        dim("path_id", "Path ID"), dim("path_order", "Path order", "integer", "ordinal"), dim("row_type", "Row type"),
        dim("display_name", "Person"), mea("x", "x"), mea("y", "y"), mea("tie_emails", "Emails on tie", "integer"),
        dim("tie_type", "Tie type"), dim("community_link", "Community link"), dim("community", "Community"),
        dim("role_group", "Role group"), mea("betweenness", "Betweenness centrality"),
        mea("contacts", "Contacts (degree)", "integer"),
    ], calcs=[
        Calc("Calculation_3000000000000000001", "x (people layer)", "real", "measure", "quantitative", "[x]"),
        keep("Calculation_3000000000000000002", "Keep row (ties, community)",
             '([row_type] = "Person" OR [Parameters].[Parameter 4] = "All ties" OR [tie_type] = "Strong (two-way)") '
             f'AND ([Parameters].[Parameter 5] = "{ALL_COMMS}" OR [community] = [Parameters].[Parameter 5])'),
    ]),
    "monthly": dict(caption="Monthly locality test", file="monthly_locality_long.csv", cols=[
        dim("month", "Month", "date", "ordinal"), dim("reliable", "Reliable month"),
        mea("active_people", "Active people", "integer"), dim("metric", "Metric"), mea("value", "Probability"),
    ], calcs=[]),
    "events": dict(caption="Key events", file="events.csv", cols=[
        dim("event_no", "#", "integer", "ordinal"), dim("date", "Date", "date", "ordinal"), dim("event", "Event"),
        dim("category", "Category"), dim("date_label", "When"),
    ], calcs=[]),
}
for k, d in DS.items():
    d["name"] = "federated." + stable_id("ds-" + k)
    d["conn"] = "textscan." + stable_id("conn-" + k)
    d["stem"] = d["file"].rsplit(".", 1)[0]
    d["object_id"] = f"{d['file']}_{hashlib.md5(k.encode()).hexdigest().upper()}"
    d["fields"] = {c.name: c for c in d["cols"] + d["calcs"]}

COLOUR_MAPS = {"deliveries": [("period", PERIOD_COLOURS)],
               "employees": [("community", None), ("role_group", "roles")],
               "network": [("community", None), ("tie_type", TIE_COLOURS), ("role_group", "roles")],
               "monthly": [("metric", METRIC_COLOURS)], "events": []}
COLOUR_FIELDS = {k: [f for f, _ in v] for k, v in COLOUR_MAPS.items()}

REMOTE = {"integer": ("20", "Sum"), "real": ("5", "Sum"), "string": ("129", "Count"),
          "date": ("133", "Year"), "datetime": ("135", "Year")}
PREFIX = {"None": "none", "Sum": "sum", "Avg": "avg", "CountD": "ctd", "Count": "cnt", "User": "usr",
          "Week-Trunc": "twk", "Month-Trunc": "tmn"}
SUFFIX = {"nominal": "nk", "ordinal": "ok", "quantitative": "qk"}


class Inst:
    """A column-instance: a field with a derivation, e.g. SUM(Deliveries) -> [sum:Calculation_...:qk]."""

    def __init__(self, ds, field, derivation="None", type_=None):
        self.ds, self.field, self.derivation = ds, field, derivation
        col = DS[ds]["fields"][field]
        self.col = col
        if type_ is None:
            type_ = "quantitative" if derivation != "None" or col.role == "measure" else col.type
        self.type = type_
        self.name = f"[{PREFIX[derivation]}:{field}:{SUFFIX[type_]}]"

    @property
    def qual(self):
        return f"[{DS[self.ds]['name']}].{self.name}"


def params_in(formula):
    return sorted(set(re.findall(r"\[Parameters\]\.\[(Parameter \d+)\]", formula)))


# ----------------------------------------------------------------------------------------------- XML helpers
def SE(parent, tag, attrib=None, text=None, **kw):
    a = dict(attrib or {})
    a.update({k.replace("__", "-"): v for k, v in kw.items()})
    el = ET.SubElement(parent, tag, {k: str(v) for k, v in a.items()})
    if text is not None:
        el.text = text
    return el


def column_el(parent, c):
    a = {}
    if c.caption:
        a["caption"] = c.caption
    a["datatype"] = c.datatype
    if c.fmt:
        a["default-format"] = c.fmt
    a.update({"name": f"[{c.name}]", "role": c.role, "type": c.type})
    el = SE(parent, "column", a)
    if isinstance(c, Calc):
        SE(el, "calculation", {"class": "tableau", "formula": c.formula})
    return el


def param_column_el(parent, pname):
    caption, default, members = PARAMS[pname]
    col = SE(parent, "column", {"caption": caption, "datatype": "string", "name": f"[{pname}]",
                                "param-domain-type": "list", "role": "measure", "type": "nominal",
                                "value": q(default)})
    SE(col, "calculation", {"class": "tableau", "formula": q(default)})
    mem = SE(col, "members")
    for m in members:
        SE(mem, "member", value=q(m))
    return col


def relation_el(parent, d, tag="relation"):
    rel = SE(parent, tag, connection=d["conn"], name=d["file"], table=f"[{d['stem']}#csv]", type="table")
    cols = SE(rel, "columns", {"character-set": "UTF-8", "header": "yes", "locale": "en_US", "separator": ","})
    for i, c in enumerate(d["cols"]):
        SE(cols, "column", datatype=c.datatype, name=c.name, ordinal=i)
    return rel


def colour_map(parent, field_inst_name, mapping):
    enc = SE(parent, "encoding", attr="color", field=field_inst_name, type="palette")
    for value, colour in mapping.items():
        m = SE(enc, "map", to=colour)
        SE(m, "bucket", text=q(value))


def datasource_el(parent, key):
    d = DS[key]
    ds = SE(parent, "datasource", caption=d["caption"], inline="true", name=d["name"], version=VERSION)
    conn = SE(ds, "connection", {"class": "federated"})
    ncs = SE(conn, "named-connections")
    nc = SE(ncs, "named-connection", caption=d["stem"], name=d["conn"])
    SE(nc, "connection", {"class": "textscan", "directory": DATA_DIR, "filename": d["file"], "password": "",
                          "server": ""})
    relation_el(conn, d, OM_F + "relation")
    relation_el(conn, d, OM_T + "relation")
    mrs = SE(conn, "metadata-records")
    cap = SE(mrs, "metadata-record", {"class": "capability"})
    SE(cap, "remote-name", text="")
    SE(cap, "remote-type", text="0")
    SE(cap, "parent-name", text=f"[{d['file']}]")
    SE(cap, "remote-alias", text="")
    SE(cap, "aggregation", text="Count")
    SE(cap, "contains-null", text="true")
    attrs = SE(cap, "attributes")
    for n, v in (("character-set", "UTF-8"), ("collation", "en_US"), ("field-delimiter", ","),
                 ("header-row", "true"), ("locale", "en_US"), ("single-char", "")):
        SE(attrs, "attribute", datatype="string", name=n, text=q(v))
    for i, c in enumerate(d["cols"]):
        rt, agg = REMOTE[c.datatype]
        mr = SE(mrs, "metadata-record", {"class": "column"})
        SE(mr, "remote-name", text=c.name)
        SE(mr, "remote-type", text=rt)
        SE(mr, "local-name", text=f"[{c.name}]")
        SE(mr, "parent-name", text=f"[{d['file']}]")
        SE(mr, "remote-alias", text=c.name)
        SE(mr, "ordinal", text=str(i))
        SE(mr, "local-type", text=c.datatype)
        SE(mr, "aggregation", text=agg)
        if c.datatype == "string":
            SE(mr, "scale", text="1")
            SE(mr, "width", text="1073741823")
        SE(mr, "contains-null", text="true")
        if c.datatype == "string":
            SE(mr, "collation", flag="0", name="LEN_RUS")
        SE(mr, OM_T + "object-id", text=f"[{d['object_id']}]")
    SE(ds, "aliases", enabled="yes")
    for c in d["cols"] + d["calcs"]:
        column_el(ds, c)
    SE(ds, TT_T + "column", caption=d["stem"], datatype="table",
       name=f"[__tableau_internal_object_id__].[{d['object_id']}]", role="measure", type="quantitative")
    for field in COLOUR_FIELDS[key]:              # colour maps below only apply to declared field instances
        SE(ds, "column-instance", column=f"[{field}]", derivation="None", name=f"[none:{field}:nk]", pivot="key",
           type="nominal")
    SE(ds, "layout", {SV_F + "dim-percentage": "0.5", SV_F + "measure-percentage": "0.4",
                      "dim-ordering": "alphabetic", "measure-ordering": "alphabetic", "show-structure": "true"})
    maps = COLOUR_MAPS[key]
    if maps:
        style = SE(ds, "style")
        rule = SE(style, "style-rule", element="mark")
        src = pd.read_csv(SRC / d["file"])
        for field, mapping in maps:
            if mapping is None:
                vals = sorted(src[field].unique(), key=lambda c: int(c.split()[0][1:]))
                mapping = {v: (COMMUNITY_COLOURS[int(v.split()[0][1:]) - 1] if not v.startswith("C0")
                               else "#b9bec8") for v in vals}
            elif mapping == "roles":
                mapping = {v: ROLE_COLOURS[i] for i, v in enumerate(sorted(src[field].unique()))}
            colour_map(rule, f"[none:{field}:nk]", mapping)
    sv = SE(ds, "semantic-values")
    SE(sv, "semantic-value", key="[Country].[Name]", value=q("United States"))
    used = sorted({p for c in d["calcs"] for p in params_in(c.formula)})
    if used:                                   # calculations that read parameters declare them here, as Tableau does
        pdep = SE(ds, "datasource-dependencies", datasource="Parameters")
        for p in used:
            param_column_el(pdep, p)
    og = SE(ds, OM_T + "object-graph")
    objs = SE(og, "objects")
    obj = SE(objs, "object", caption=d["stem"], id=d["object_id"])
    props = SE(obj, "properties", context="")
    relation_el(props, d)
    return ds


def parameters_el(parent):
    ds = SE(parent, "datasource", hasconnection="false", inline="true", name="Parameters", version=VERSION)
    SE(ds, "aliases", enabled="yes")
    for p in PARAMS:
        param_column_el(ds, p)
    return ds


# ----------------------------------------------------------------------------------------------- worksheets
def deps_el(view, ds_key, insts, extra_fields=()):
    d = DS[ds_key]
    dep = SE(view, "datasource-dependencies", datasource=d["name"])
    fields = []
    pending = [i.field for i in insts] + list(extra_fields)
    while pending:                                    # include fields referenced by calculations, recursively
        f = pending.pop(0)
        if f in fields:
            continue
        fields.append(f)
        col = d["fields"][f]
        if isinstance(col, Calc):
            pending += [g for g in d["fields"] if f"[{g}]" in col.formula]
    for f in sorted(fields):
        column_el(dep, d["fields"][f])
    done = set()
    for i in sorted(insts, key=lambda i: i.name):
        if i.name in done:
            continue
        done.add(i.name)
        SE(dep, "column-instance", column=f"[{i.field}]", derivation=i.derivation, name=i.name, pivot="key",
           type=i.type)
    return dep, fields


def members_filter(view, inst, members):
    f = SE(view, "filter", {"class": "categorical", "column": inst.qual})
    SE(f, "groupfilter", {"function": "member", "level": inst.name, "member": q(members[0]),
                          U + "ui-domain": "database", U + "ui-enumeration": "inclusive",
                          U + "ui-marker": "enumerate"})


def range_filter(view, inst, lo, hi):
    f = SE(view, "filter", {"class": "quantitative", "column": inst.qual, "included-values": "in-range"})
    SE(f, "min", text=str(lo))
    SE(f, "max", text=str(hi))


def title_el(parent, text, sub=None):
    lo = SE(parent, "layout-options")
    t = SE(lo, "title")
    ft = SE(t, "formatted-text")
    SE(ft, "run", bold="true", fontcolor=INK, fontsize="12", text=text)
    if sub:
        SE(ft, "run", text="Æ\n")
        SE(ft, "run", fontcolor=MUTED, fontsize="9", text=sub)


class Sheet:
    def __init__(self, name, ds, title, sub=None):
        self.name, self.ds, self.title, self.sub = name, ds, title, sub
        self.insts, self.filters, self.slices, self.panes = [], [], [], []
        self.rows = self.cols = ""
        self.axis_rules, self.extra_style = [], []

    def inst(self, field, derivation="None", type_=None):
        i = Inst(self.ds, field, derivation, type_)
        self.insts.append(i)
        return i

    def xml(self, parent):
        ws = SE(parent, "worksheet", name=self.name)
        title_el(ws, self.title, self.sub)
        table = SE(ws, "table")
        view = SE(table, "view")
        dss = SE(view, "datasources")
        tmp = ET.Element("tmp")                       # collect field list first to know which parameters are used
        _, fields = deps_el(tmp, self.ds, self.insts)
        used = sorted({p for f in fields if isinstance(DS[self.ds]["fields"][f], Calc)
                       for p in params_in(DS[self.ds]["fields"][f].formula)})
        SE(dss, "datasource", caption=DS[self.ds]["caption"], name=DS[self.ds]["name"])   # primary first
        if used:
            SE(dss, "datasource", name="Parameters")
        if used:
            pdep = SE(view, "datasource-dependencies", datasource="Parameters")
            for p in used:
                param_column_el(pdep, p)
        deps_el(view, self.ds, self.insts)
        for f in self.filters:
            f(view)
        if self.slices:
            sl = SE(view, "slices")
            for s in self.slices:
                SE(sl, "column", text=s.qual)
        SE(view, "aggregation", value="true")
        style = SE(table, "style")
        if self.axis_rules:
            r = SE(style, "style-rule", element="axis")
            for a in self.axis_rules:
                a = dict(a)
                SE(r, a.pop("_tag", "encoding"), a)
        for element, formats in self.extra_style:
            r = SE(style, "style-rule", element=element)
            for f in formats:
                SE(r, "format", f)
        panes = SE(table, "panes")
        for p in self.panes:
            a = {}
            if "id" in p:
                a["id"] = p["id"]
            a["selection-relaxation-option"] = "selection-relaxation-allow"
            if "x-axis-name" in p:
                a["x-axis-name"] = p["x-axis-name"]
            pane = SE(panes, "pane", a)
            pv = SE(pane, "view")
            SE(pv, "breakdown", value="auto")
            SE(pane, "mark", {"class": p.get("mark", "Automatic")})
            if p.get("enc"):
                enc = SE(pane, "encodings")
                for tag, inst in p["enc"]:
                    SE(enc, tag, column=inst.qual)
            if p.get("label"):
                cl = SE(pane, "customized-label")
                ft = SE(cl, "formatted-text")
                for run in p["label"]:
                    SE(ft, "run", run[1], text=run[0])
            if p.get("formats"):
                ps = SE(pane, "style")
                r = SE(ps, "style-rule", element="mark")
                for k, v in p["formats"]:
                    SE(r, "format", attr=k, value=v)
        SE(table, "rows", text=self.rows or None)
        SE(table, "cols", text=self.cols or None)
        SE(ws, "simple-id", uuid=guid("ws-" + self.name))
        return ws


def build_sheets():
    sheets = []
    D = "deliveries"

    def deliveries_filter(s):
        k = s.inst("Calculation_1000000000000000003")
        s.filters.append(lambda v, i=k: members_filter(v, i, ["Keep"]))
        s.slices.append(k)

    kpis = [("KPI Deliveries", "Calculation_1000000000000000001", "Sum", "deliveries (sender → recipient)"),
            ("KPI Messages", "message_id", "CountD", "unique messages"),
            ("KPI Senders", "sender", "CountD", "active senders"),
            ("KPI Cross-community", "Calculation_1000000000000000002", "User", "of email crosses communities")]
    for name, field, der, label in kpis:
        s = Sheet(name, D, name.replace("KPI ", ""))
        m = s.inst(field, der, "quantitative")
        deliveries_filter(s)
        s.panes.append(dict(mark="Text", enc=[("text", m)], label=[
            (f"<{m.qual}>", {"bold": "true", "fontcolor": "#1f3864", "fontsize": "24"}),
            ("Æ\n", {}), (label, {"fontcolor": MUTED, "fontsize": "10"})],
            formats=[("mark-labels-show", "true")]))
        sheets.append(s)

    s = Sheet("Email Volume Timeline", D, "Weekly email deliveries, 1999-2002",
              "Colour = period. Volume more than triples in the crisis window (Aug-Dec 2001).")
    wk, n, per = (s.inst("sent_at", "Week-Trunc", "quantitative"), s.inst("Calculation_1000000000000000001", "Sum"),
                  s.inst("period"))
    deliveries_filter(s)
    s.panes.append(dict(mark="Area", enc=[("color", per)]))
    s.rows, s.cols = n.qual, wk.qual
    s.axis_rules = [{"_tag": "format", "attr": "title", "class": "0", "field": wk.qual, "scope": "cols", "value": "Week"}]
    sheets.append(s)

    s = Sheet("Communication Flow by Role", D, "Who emails whom, by seniority",
              "Rows = sender role, columns = recipient role; darker = more deliveries.")
    sr, rr, n = s.inst("sender_role"), s.inst("recipient_role"), s.inst("Calculation_1000000000000000001", "Sum")
    deliveries_filter(s)
    s.panes.append(dict(mark="Square", enc=[("color", n), ("text", n)]))
    s.rows, s.cols = sr.qual, rr.qual
    sheets.append(s)

    s = Sheet("Key Events", "events", "Key events in the Enron collapse")
    no, when, ev = s.inst("event_no"), s.inst("date_label"), s.inst("event")
    s.panes.append(dict(mark="Text", enc=[("text", ev)]))
    s.rows = f"({no.qual} / {when.qual})"
    sheets.append(s)

    s = Sheet("Locality Test by Month", "monthly", "Unit-5 locality test: is this a social network?",
              "Upper line: P(y-z tie | x-y and x-z ties). Lower line: edge density (what chance alone gives).")
    mon, val, met, rel = (s.inst("month", "Month-Trunc", "quantitative"), s.inst("value", "Sum"),
                          s.inst("metric"), s.inst("reliable"))
    s.filters.append(lambda v, i=rel: members_filter(v, i, ["Yes"]))
    s.slices.append(rel)
    s.panes.append(dict(mark="Line", enc=[("color", met)]))
    s.rows, s.cols = val.qual, mon.qual
    s.axis_rules = [{"_tag": "format", "attr": "title", "class": "0", "field": mon.qual, "scope": "cols", "value": "Month"}]
    sheets.append(s)

    s = Sheet("Network Graph", "network", "Email network (Girvan-Newman communities)",
              "Node = person (size = betweenness, colour = community); line = email tie.")
    x, x2, y = s.inst("x", "Avg"), s.inst("Calculation_3000000000000000001", "Avg"), s.inst("y", "Avg")
    pid, order, person = s.inst("path_id"), s.inst("path_order"), s.inst("display_name")
    tie, comm, btw = s.inst("tie_type"), s.inst("community"), s.inst("betweenness", "Avg")
    role, contacts, k = s.inst("role_group"), s.inst("contacts", "Avg"), s.inst("Calculation_3000000000000000002")
    s.filters.append(lambda v, i=k: members_filter(v, i, ["Keep"]))
    s.slices.append(k)
    s.panes += [dict(mark="Automatic"),
                {"id": "1", "x-axis-name": x.qual, "mark": "Line",
                 "enc": [("color", tie), ("lod", pid), ("path", order)], "formats": [("size", "0.2")]},
                {"id": "2", "x-axis-name": x2.qual, "mark": "Circle",
                 "enc": [("color", comm), ("size", btw), ("tooltip", role), ("tooltip", contacts), ("lod", person)],
                 "formats": [("mark-transparency", "235")]}]
    s.rows, s.cols = y.qual, f"({x.qual} + {x2.qual})"
    s.axis_rules = [
        {"attr": "space", "class": "0", "field": x2.qual, "field-type": "quantitative", "fold": "true",
         "scope": "cols", "synchronized": "true", "type": "space"},
        {"attr": "space", "class": "0", "field": x.qual, "field-type": "quantitative", "max": "104", "min": "-4",
         "range-type": "fixed", "scope": "cols", "type": "space"},
        {"attr": "space", "class": "0", "field": y.qual, "field-type": "quantitative", "max": "104", "min": "-4",
         "range-type": "fixed", "scope": "rows", "type": "space"},
        {"_tag": "format", "attr": "display", "class": "0", "field": x.qual, "scope": "cols", "value": "false"},
        {"_tag": "format", "attr": "display", "class": "0", "field": x2.qual, "scope": "cols", "value": "false"},
        {"_tag": "format", "attr": "display", "class": "0", "field": y.qual, "scope": "rows", "value": "false"},
    ]
    s.extra_style.append(("gridline", [{"attr": "line-visibility", "scope": "cols", "value": "off"},
                                       {"attr": "line-visibility", "scope": "rows", "value": "off"}]))
    s.extra_style.append(("zeroline", [{"attr": "line-visibility", "scope": "cols", "value": "off"},
                                       {"attr": "line-visibility", "scope": "rows", "value": "off"}]))
    sheets.append(s)

    s = Sheet("Top People", "employees", "Top 15 people by the selected metric",
              "Change the metric with 'Rank people by'. Executives keep real names; others are pseudonyms.")
    label, metric, rank = (s.inst("Calculation_2000000000000000003"), s.inst("Calculation_2000000000000000001", "Sum"),
                           s.inst("Calculation_2000000000000000002"))
    role, person = s.inst("role_group"), s.inst("display_name")
    s.filters.append(lambda v, i=rank: range_filter(v, i, 1, 15))
    s.slices.append(rank)
    s.panes.append(dict(mark="Bar", enc=[("color", role), ("lod", person)],
                        formats=[("mark-labels-show", "true")]))
    s.rows, s.cols = label.qual, metric.qual
    sheets.append(s)

    s = Sheet("Community Composition", "employees", "Who is in each community",
              "People per Girvan-Newman community, coloured by role group.")
    comm, cnt, role = s.inst("community"), s.inst("employee_key", "Count", "quantitative"), s.inst("role_group")
    s.panes.append(dict(mark="Bar", enc=[("color", role)]))
    s.rows, s.cols = comm.qual, cnt.qual
    sheets.append(s)
    return sheets


# ----------------------------------------------------------------------------------------------- dashboards
class Z:
    """Layout tree: containers split their rectangle horizontally or vertically by fixed pixel sizes."""

    def __init__(self, kind, size=None, children=(), **attrs):
        self.kind, self.size, self.children, self.attrs = kind, size, list(children), attrs


def place(z, x, y, w, h):
    z.rect = (x, y, w, h)
    if z.kind in ("horz", "vert"):
        fixed = sum(c.size for c in z.children if c.size)
        flex = [c for c in z.children if not c.size]
        total = w if z.kind == "horz" else h
        rest = max(total - fixed, 0) / max(len(flex), 1)
        pos = x if z.kind == "horz" else y
        for c in z.children:
            span = c.size or rest
            if z.kind == "horz":
                place(c, pos, y, span, h)
            else:
                place(c, x, pos, w, span)
            pos += span


def emit(parent, z, W, H, ids):
    x, y, w, h = z.rect
    a = {"h": round(h / H * 100000), "id": next(ids)}
    if z.kind in ("horz", "vert"):
        a.update({"param": z.kind, "type": "layout-flow"})
    elif z.kind == "sheet":
        a["name"] = z.attrs["name"]
    elif z.kind == "text":
        a["type"] = "text"
    elif z.kind == "param":
        a.update({"mode": "compact", "param": f"[Parameters].[{z.attrs['param']}]", "type": "paramctrl"})
    elif z.kind == "color":
        a["name"] = z.attrs["name"]
        if "pane" in z.attrs:
            a["pane-specification-id"] = z.attrs["pane"]
        a.update({"param": z.attrs["param"], "type": "color"})
    a.update({"w": round(w / W * 100000), "x": round(x / W * 100000), "y": round(y / H * 100000)})
    el = SE(parent, "zone", a)
    if z.kind == "text":
        ft = SE(el, "formatted-text")
        for text, fmt in z.attrs["runs"]:
            SE(ft, "run", fmt, text=text)
    for c in z.children:
        emit(el, c, W, H, ids)
    zs = SE(el, "zone-style")
    SE(zs, "format", attr="border-color", value="#000000")
    SE(zs, "format", attr="border-style", value="none")
    SE(zs, "format", attr="border-width", value="0")
    SE(zs, "format", attr="margin", value="4" if z.kind not in ("horz", "vert") else "0")
    return el


def dashboard_el(parent, name, W, H, layout, params, legend_insts):
    db = SE(parent, "dashboard", name=name)
    SE(db, "style")
    SE(db, "size", maxheight=H, maxwidth=W, minheight=H, minwidth=W)
    dss = SE(db, "datasources")
    SE(dss, "datasource", name="Parameters")
    pdep = SE(db, "datasource-dependencies", datasource="Parameters")
    for p in params:
        param_column_el(pdep, p)
    zones = SE(db, "zones")
    place(layout, 0, 0, W, H)
    ids = iter(range(3, 1000))
    top = SE(zones, "zone", {"h": "100000", "id": "2", "type": "layout-basic", "w": "100000", "x": "0", "y": "0"})
    emit(top, layout, W, H, ids)
    zs = SE(top, "zone-style")
    SE(zs, "format", attr="border-color", value="#000000")
    SE(zs, "format", attr="border-style", value="none")
    SE(zs, "format", attr="border-width", value="0")
    SE(zs, "format", attr="margin", value="8")
    SE(db, "simple-id", uuid=guid("db-" + name))
    return db


def text_runs(title, sub):
    return [(title, {"bold": "true", "fontcolor": INK, "fontsize": "17"}), ("Æ\n", {}),
            (sub, {"fontcolor": MUTED, "fontsize": "10"})]


def build_dashboards(parent):
    per = Inst("deliveries", "period")
    comm = Inst("network", "community")
    W, H = 1300, 820
    overview = Z("vert", children=[
        Z("text", 66, runs=text_runs(
            "Enron's email network, 1999-2002: how communication changed as the company collapsed",
            "34,374 de-duplicated deliveries among 148 employees (Enron corpus, FERC/DoJ release). "
            "Junior staff are pseudonymised; only metadata (who-whom-when) is used.")),
        Z("horz", 104, children=[Z("sheet", name="KPI Deliveries"), Z("sheet", name="KPI Messages"),
                                 Z("sheet", name="KPI Senders"), Z("sheet", name="KPI Cross-community")]),
        Z("horz", children=[
            Z("vert", children=[Z("sheet", 330, name="Email Volume Timeline"),
                                Z("horz", children=[Z("sheet", name="Communication Flow by Role"),
                                                    Z("sheet", name="Locality Test by Month")])]),
            Z("vert", 400, children=[
                Z("param", 60, param="Parameter 2"),
                Z("param", 60, param="Parameter 3"),
                Z("color", 92, name="Email Volume Timeline", param=per.qual),
                Z("sheet", name="Key Events")]),
        ]),
    ])
    dashboard_el(parent, "1 Overview", W, H, overview, ["Parameter 2", "Parameter 3"], [per])

    network = Z("vert", children=[
        Z("text", 66, runs=text_runs(
            "Who holds the network together? Communities and brokers",
            "Girvan-Newman communities on two-way (strong) ties; brokers = high betweenness. "
            "Click a bar to highlight that person in the graph.")),
        Z("horz", children=[
            Z("vert", children=[Z("sheet", name="Network Graph")]),
            Z("vert", 470, children=[
                Z("horz", 60, children=[Z("param", param="Parameter 1"), Z("param", param="Parameter 5"),
                                        Z("param", param="Parameter 4")]),
                Z("sheet", 400, name="Top People"),
                Z("sheet", name="Community Composition")]),
        ]),
        Z("color", 46, name="Network Graph", param=comm.qual, pane="2"),
    ])
    dashboard_el(parent, "2 Network", W, H, network, ["Parameter 1", "Parameter 4", "Parameter 5"], [comm])


def actions_el(parent):
    acts = SE(parent, "actions")
    for n, (caption, dashboard, field) in enumerate((("Highlight person", "2 Network", "Person"),
                                                     ("Highlight period", "1 Overview", "Period")), 1):
        a = SE(acts, "action", caption=caption,
               name=f"[Action{n}_" + stable_id(f"act{n}", 32, "0123456789ABCDEF") + "]")
        SE(a, "activation", {"auto-clear": "true", "type": "on-select"})
        SE(a, "source", dashboard=dashboard, type="sheet")
        cmd = SE(a, "command", command="tsc:brush")
        SE(cmd, "param", name="field-captions", value=field)
        SE(cmd, "param", name="target", value=dashboard)


def windows_el(parent, sheets):
    wins = SE(parent, "windows", source__height="30")
    for name, views in (("1 Overview", ["KPI Deliveries", "KPI Messages", "KPI Senders", "KPI Cross-community",
                                        "Email Volume Timeline", "Communication Flow by Role", "Key Events",
                                        "Locality Test by Month"]),
                        ("2 Network", ["Network Graph", "Top People", "Community Composition"])):
        a = {"class": "dashboard"}
        if name == "1 Overview":
            a["maximized"] = "true"
        a["name"] = name
        w = SE(wins, "window", a)
        vps = SE(w, "viewpoints")
        for v in views:
            SE(vps, "viewpoint", name=v)
        SE(w, "active", id="-1")
        SE(w, "simple-id", uuid=guid("win-" + name))
    for s in sheets:
        w = SE(wins, "window", {"class": "worksheet", "name": s.name})
        cards = SE(w, "cards")
        left = SE(cards, "edge", name="left")
        st = SE(left, "strip", size="160")
        for t in ("pages", "filters", "marks"):
            SE(st, "card", type=t)
        top = SE(cards, "edge", name="top")
        for t in ("columns", "rows"):
            SE(SE(top, "strip", size="2147483647"), "card", type=t)
        SE(SE(top, "strip", size="31"), "card", type="title")
        SE(w, "simple-id", uuid=guid("win-" + s.name))


def build():
    root = ET.Element("workbook", {"original-version": VERSION, "source-build": SOURCE_BUILD,
                                   "source-platform": "win", "version": VERSION}, nsmap={"user": USER})
    man = SE(root, "document-format-change-manifest")
    for feat in ("_.fcp.ObjectModelEncapsulateLegacy.true...ObjectModelEncapsulateLegacy",
                 "_.fcp.ObjectModelTableType.true...ObjectModelTableType",
                 "_.fcp.SchemaViewerObjectModel.true...SchemaViewerObjectModel",
                 "SheetIdentifierTracking", "WindowsPersistSimpleIdentifiers"):
        SE(man, feat)
    prefs = SE(root, "preferences")
    SE(prefs, "preference", name="ui.encoding.shelf.height", value="24")
    SE(prefs, "preference", name="ui.shelf.height", value="26")
    dss = SE(root, "datasources")
    parameters_el(dss)
    for k in DS:
        datasource_el(dss, k)
    actions_el(root)
    sheets = build_sheets()
    wss = SE(root, "worksheets")
    for s in sheets:
        s.xml(wss)
    dbs = SE(root, "dashboards")
    build_dashboards(dbs)
    windows_el(root, sheets)
    return ET.ElementTree(root)


def main():
    tree = build()
    twb = HERE / f"{NAME}.twb"
    tree.write(str(twb), xml_declaration=True, encoding="utf-8", pretty_print=True)
    data = HERE / DATA_DIR
    data.mkdir(parents=True, exist_ok=True)
    for d in DS.values():
        shutil.copy(SRC / d["file"], data / d["file"])
    twbx = HERE / f"{NAME}.twbx"
    with zipfile.ZipFile(twbx, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(twb, twb.name)
        for d in DS.values():
            z.write(data / d["file"], f"{DATA_DIR}/{d['file']}")
    print("wrote", twb.relative_to(ROOT), "and", twbx.relative_to(ROOT), f"({twbx.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
