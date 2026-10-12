# CostWeave live StudioNet evidence

- Contract: `0x9B5193244a8a97A2f94d09eF2B1F9697c34f0741`
- Network: GenLayer StudioNet 61999
- Owner wallet A: `0xeb57bc7125fa60d7482ce12058397369ab3581f8`
- Reviewer/consumer wallet B: `0x2da5393d7bbb9a037dc3abb56dbbc5c150fc843f`
- Main/deployer wallet participation after deployment: none
- Result: 14/14 transactions finalized with expected execution; 26/26 assertions passed
- Full receipts and exact pre/post state: `docs/live-evidence/studionet-261012.json`

## Finalized transaction trail

| Case | Expected execution | Transaction hash |
|---|---|---|
| Create denomination-bound happy batch | SUCCESS | [0x8035471c3ee7cab0c795d04de8a2ee6ee77e4f3d4e212ed81f21c2498c27f395](https://explorer-studio.genlayer.com/tx/0x8035471c3ee7cab0c795d04de8a2ee6ee77e4f3d4e212ed81f21c2498c27f395) |
| Reject owner acting as reviewer | ERROR | [0x63a9e2c470468f58d12f20d985241d80e190eecc31c271414b2a0ca36c1fb09b](https://explorer-studio.genlayer.com/tx/0x63a9e2c470468f58d12f20d985241d80e190eecc31c271414b2a0ca36c1fb09b) |
| Reject wrong snapshot | ERROR | [0x76478319df606a77045d0658c809f83db4fcb334404015c9c476ee9dde8fb232](https://explorer-studio.genlayer.com/tx/0x76478319df606a77045d0658c809f83db4fcb334404015c9c476ee9dde8fb232) |
| Reviewer accepts exact snapshot | SUCCESS | [0x27162ad1592bcd8c26f92d708d8d4538654a86c8b870fb2d74f3296e69812a3a](https://explorer-studio.genlayer.com/tx/0x27162ad1592bcd8c26f92d708d8d4538654a86c8b870fb2d74f3296e69812a3a) |
| Reject changed source digest | ERROR | [0x5f0aaf29e7a694ee37bdb41438da1f97ec950fc49a434e962245d396b8982e60](https://explorer-studio.genlayer.com/tx/0x5f0aaf29e7a694ee37bdb41438da1f97ec950fc49a434e962245d396b8982e60) |
| Compile happy allocation | SUCCESS | [0xa39ee937628d4f121d945ae942190dfb4cf4e61038284c219134bc87ff0f2929](https://explorer-studio.genlayer.com/tx/0xa39ee937628d4f121d945ae942190dfb4cf4e61038284c219134bc87ff0f2929) |
| Reject generation replay | ERROR | [0xa6979dcbae966a17d5f0922635e0a0c5746cbd4c3e41b084abb868fa6afbda50](https://explorer-studio.genlayer.com/tx/0xa6979dcbae966a17d5f0922635e0a0c5746cbd4c3e41b084abb868fa6afbda50) |
| Reject wrong consumer | ERROR | [0x74506e6f624465304a517a0a6646f4b7289cd8f810dfd1525b1307d4eb37d59a](https://explorer-studio.genlayer.com/tx/0x74506e6f624465304a517a0a6646f4b7289cd8f810dfd1525b1307d4eb37d59a) |
| Reviewer/consumer consumes once | SUCCESS | [0xcf3f689112add9694121fe6e6a4272d216b0ce8d710e1227b8a66d71d4f73354](https://explorer-studio.genlayer.com/tx/0xcf3f689112add9694121fe6e6a4272d216b0ce8d710e1227b8a66d71d4f73354) |
| Reject double consumption | ERROR | [0x739f15877475d86fff3e13197c14f9fec98fa85729ed84f7da9765eada204201](https://explorer-studio.genlayer.com/tx/0x739f15877475d86fff3e13197c14f9fec98fa85729ed84f7da9765eada204201) |
| Create insufficient-evidence batch | SUCCESS | [0x1f2207cfb79bf97481e431999bd342cd8e8bd71f3dfe94c8c0dd78fe1633a001](https://explorer-studio.genlayer.com/tx/0x1f2207cfb79bf97481e431999bd342cd8e8bd71f3dfe94c8c0dd78fe1633a001) |
| Reviewer accepts review batch | SUCCESS | [0x88b15003689668577549794549fc57e44c0df08d8f77a71dddbb70b7570ec6dd](https://explorer-studio.genlayer.com/tx/0x88b15003689668577549794549fc57e44c0df08d8f77a71dddbb70b7570ec6dd) |
| Compile insufficient evidence | SUCCESS | [0xd1701c93e6b2060fd19df8e2a81c4706d8b698105165684638b41550269a39ca](https://explorer-studio.genlayer.com/tx/0xd1701c93e6b2060fd19df8e2a81c4706d8b698105165684638b41550269a39ca) |
| Reject consuming review-required result | ERROR | [0xc1b3390c1724e00fc24282091ccb1a6118636abd3bd188180e1e1ef18c2fce77](https://explorer-studio.genlayer.com/tx/0xc1b3390c1724e00fc24282091ccb1a6118636abd3bd188180e1e1ef18c2fce77) |

## Authoritative post-state

The happy batch finalized as `CONSUMED`, generation `1`, denomination `USD_CENTS`,
source digest `649504d4ff4c3d1d57893b4fe7b68937239b22f65c16e23c9349c870eee96947`,
and conserved `140 = 140 allowable + 0 unallowable + 0 review`.

The insufficient-evidence batch finalized as `REVIEW_REQUIRED`, generation `1`,
with `25 = 0 allowable + 0 unallowable + 25 review`; consumption was finalized as
an expected business error with exact state unchanged.

Expected `ERROR` receipts demonstrate rejected contract actions, not successful
state changes. Each is paired with exact pre/post equality in the machine report.
This run does not claim a deliberately induced live validator no-consensus event.
