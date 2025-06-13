#!/bin/bash
set -e

python3 -m venv idrawaptt
source idrawaptt/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

cat << 'EOF'

#.___  ________                           _____ _____________________
#|   | \______ \____________ __  _  __   /  _  \\______   \__    ___/
#|   |  |    |  \_  __ \__  \\ \/ \/ /  /  /_\  \|     ___/ |    |   
#|   |  |    `   \  | \// __ \\     /  /    |    \    |     |    |   
#|___| /_______  /__|  (____  /\/\_/   \____|__  /____|ver1 |____|   
#              \/           \/                 \/                   
#
┌───────────────────────────────────────────────────────────────┐
│ >>> [ D4RKCYD3R CR3W ] - 1NST4LL4T10N D0N3, H4X0R! <<<        │
│ >>> R3L34S3: v3r0 - [ W4R3Z 4L1V3 '25 ] <<<                  │
└───────────────────────────────────────────────────────────────┘
┌───────────────────────────────────────────────────────────────┐
│ >>> N3XT M1SS10N, 3L1T3:                                      │
│ 1. DR0P A S1CK PNG F4V1C0N IN PR0J3CT R00T: 'favicon.png'     │
│ 2. CL0N3 .env.example T0 .env & PL4NT UR 0P3N41 K3Y (0PT10N4L)│
│ 3. BR0WS3R N0T F1R1NG? H1T 1T: streamlit run idapt.py         │
└───────────────────────────────────────────────────────────────┘
┌───────────────────────────────────────────────────────────────┐
│ >>> L00T DR0P L0C4T10N:                                       │
│ - G4LL3RY PIX ST4SH3D IN: gallery/                           │
│ - L0GZ L0CK3D IN: logs/                                      │
└───────────────────────────────────────────────────────────────┘
┌───────────────────────────────────────────────────────────────┐
│ >>> SH0UTZ: SH4D0WPH4NT0M, CYB3RZ3R0, 4LL W4R3Z BR0Z         │
│ >>> K33P TH3 N3T FR33, ST4Y 4N0N, N3V3R G3T PWN3D!           │
└───────────────────────────────────────────────────────────────┘
#
# [ END TR4NSM1SS10N - D4RKCYD3R W4R3Z CR3W - 0WN1NG S1NC3 '92 ]
#
EOF

source idrawaptt/bin/activate
idrawaptt/bin/python -m streamlit run idapt.py --server.address 0.0.0.0 --server.port 1337