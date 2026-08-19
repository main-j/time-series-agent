# Scripted Routing Flow on Real MMTS

PASS 1/4

- `Base:synthtic_qa_700:3` (Base): roles=['matching'] tools=4 -> FAIL ["Base roles ['matching']"]
- `InWild:tsqa_1084:1` (InWild): roles=['matching'] tools=4 -> FAIL ["InWild roles ['matching']"]
- `Match:qats_400:200` (Match): roles=['matching'] tools=4 -> PASS
- `Align:ts2caption_qa_120:0` (Align): roles=['matching'] tools=4 -> FAIL ["Align roles ['matching']"]