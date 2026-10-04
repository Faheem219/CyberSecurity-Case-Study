# G04 – Video Presentation Script

**Topic:** Non-Human Identity and Scoped Delegation for Intrusion Detection and Forensic Attribution of AI-Orchestrated Attacks: A Case Study of the GTG-1002 Espionage Campaign (2025)

**Deck:** `G04_Presentation.html` (17 slides). Open it in Chrome and press **F** for full screen. Use **→ / Space** for the next slide and **←** to go back. The arrows only show when you hover at the left or right edge.

**Target length:** about 8.0 minutes in total (1123 words at a normal speaking pace of ~140 words per minute). Keep your camera on while you speak.

**How the split was made:** each person presents one continuous block of the report, and each block covers about a third of the report's words. Within a block, each slide's share of the script follows the size of the report section it covers.

| Speaker | Slides | Report sections covered | Report words | Script words | Approx. time |
|---|---|---|---|---|---|
| Raghav Sonchhatra | 1–5 | Abstract, 1 Introduction (1.1, 1.2), 2.1–2.2 Literature Review | 931 (31%) | 359 (32%) | ~2 min 33 s |
| Sanidhya Awasthi | 6–10 | 2.3–2.5 Literature Review, 1.3 Objectives, 3 Methodology, 4 Implementation (tokens, gateway, log) | 1086 (36%) | 394 (35%) | ~2 min 48 s |
| Faheemuddin Sayyed | 11–17 | 4 Implementation (IDS rules, workload), 5 Results & Discussion, 6 Conclusion | 990 (33%) | 370 (33%) | ~2 min 38 s |

---

## Part 1 — Raghav Sonchhatra (Slides 1–5)

### Slide 1 · Title
Hello everyone, we are Group 04. I'm Raghav Sonchhatra, and with me are Sanidhya Awasthi and Faheemuddin Sayyed. Our Unit 4 case study looks at how giving AI agents their own identities and limited permissions can help with intrusion detection and forensics. It's based on a real 2025 campaign called GTG-1002.

### Slide 2 · AI agents now act
AI has moved from answering questions to actually doing things. With MCP, an agent can call tools, and with A2A, agents can talk to other agents. Each agent is a non-human identity, meaning an account that belongs to software, not a person. In companies these already outnumber humans about 82 to 1, and many of them have privileged access. The problem is that agents often share one long-lived key, and nobody records who allowed what. This links to four Unit 4 topics: intrusion detection, digital forensics, security tools like Kali and Nmap, and malware analysis.

### Slide 3 · GTG-1002 at a glance
In mid-September 2025, Anthropic detected a cyber-espionage campaign that it linked, with high confidence, to a Chinese state-sponsored group, and named it GTG-1002. It targeted about 30 organisations, like tech companies, financial firms and government agencies, and a few attacks succeeded. The AI did 80 to 90 percent of the work, and humans stepped in at only a few points. The attackers pretended to be a security company doing testing, and they used normal open-source tools, not custom malware.

### Slide 4 · How the campaign unfolded
There were six phases. Humans picked the targets. The AI then mapped the systems, collected credentials, moved between machines, gathered data and wrote handoff notes. Humans only approved the big steps. The key point is that each small task looked normal by itself. You could only see the attack by looking at all the agents together.

### Slide 5 · Literature review, part 1
We then looked at existing research. Studies like Fang's and PentestGPT showed that AI agents can carry out hacking tasks, and Greshake showed that agents can be misled through prompt injection. On the identity side, OWASP now has Top 10 lists for non-human identities and for agentic apps, and researchers have suggested agent IDs, activity logs and safer delegation. But most of this work looks at the model, not at how each action gets approved. Over to Sanidhya.

---

## Part 2 — Sanidhya Awasthi (Slides 6–10)

### Slide 6 · Literature review, part 2
Thanks, Raghav. I'm Sanidhya. The ideas behind delegation are old. Saltzer and Schroeder wrote about least privilege in 1975, and Hardy described the "confused deputy", which is a program using its own power for someone else's request. That's exactly what an AI agent does. OAuth token exchange and macaroons let us pass on limited access. For detection and forensics we have classic work like Denning's model, Snort, Zeek and the NIST guides. But no study we found connects agent identity with detection and forensics, and that's our gap.

### Slide 7 · Objectives and method
Our goals were to break GTG-1002 down phase by phase, find the identity problem behind each phase, design controls for it, and test them. We did this in four stages. First, we rebuilt the case from Anthropic's public report. Second, we mapped each phase to MITRE ATT&CK and OWASP's identity risks. Third, we designed the controls. Fourth, we ran an experiment comparing a normal setup with ours. We used synthetic data, so no real system was touched.

### Slide 8 · Each phase relied on an identity failure
This table shows stage two. For each phase we asked which identity failure made it possible. In phase one, the "security company" story wasn't tied to any real person, so in our design every grant comes from a named human. In reconnaissance, one broad credential worked everywhere, so we limit resources and watch call speed. And since each sub-task looked fine alone, every sub-agent gets its own identity, all linked through one grant.

### Slide 9 · Control design
This gave us five principles. Every agent gets its own identity with a human owner. Permissions can only get smaller when passed down. Every tool call goes through one gateway. Every decision goes into a log that can't be quietly edited. And detection rules look at the agent's identity, not just an IP address or a shared key. We chose identity because the organisation can enforce and log it by itself.

### Slide 10 · Tokens, gateway and audit log
We built this in Python, in about 500 lines. Each agent gets a signed token that records who delegated to whom, starting from the human, plus its allowed scopes, resources, expiry and depth. When an agent passes work on, the token can only shrink. If it asks for more, it's refused, and the refusal is logged. Every log entry also stores the hash of the one before it. The tools are only labels, so nothing actually runs. Faheemuddin will now take you through the results.

---

## Part 3 — Faheemuddin Sayyed (Slides 11–17)

### Slide 11 · Detection rules and the test workload
Thanks, Sanidhya. I'm Faheemuddin. We used three simple IDS rules. R1 flags an agent making more than 20 calls in 10 seconds. R2 flags three denials within a minute. R3 flags one grant touching three or more attack stages within half an hour. For testing, we simulated four normal agents, including a backup job that looks a bit like data theft on purpose, and one misuse setup with an orchestrator and five sub-agents. Each setup ran 50 times with the same rules.

### Slide 12 · Main results
Here are the results. With a shared key, nothing was blocked. With our design, 77 percent of misuse calls were blocked, and exposed production resources went from about 25 per run to zero. False alerts dropped from about two per run to zero, and every alert named the person responsible. Both setups caught the attack, but a shared-key alert only shows the key, so you'd have to stop every agent. Our checks add only about 6 microseconds per call.

### Slide 13 · Prevention by attack stage
By attack stage, credential access, lateral movement, collection and exfiltration were fully blocked. The roughly 31 calls that went through were scans on staging, which the grant allowed. So scoping limits damage, but we still need detection.

### Slide 14 · Forensic timeline
This timeline is built straight from the audit log, so you can see who did what and on whose behalf. Every misuse record traced back to the contractor, and the first alert came within seconds. When we edited one log record, the hash check caught exactly that record.

### Slide 15 · What this means for GTG-1002
In GTG-1002, the attackers ran agents on their own systems, so victims can't force tokens on them. But these controls still help. AI platforms can ask for a verified identity before "security testing", companies can protect their own agents, and targets can issue short-lived, narrow credentials so stolen ones are worth less. Our limits are synthetic data and hand-set thresholds.

### Slide 16 · Conclusion
To sum up, GTG-1002 didn't need special tools. The real problem was access that nobody had limited and nobody could trace. Separate identities, shrinking permissions and a solid log made the attack harder, the alerts cleaner and the forensics possible. Next, we'd like to test this on real logs.

### Slide 17 · Thank you
That's all from Group 04. Our full report has 41 references. Thank you for watching.
