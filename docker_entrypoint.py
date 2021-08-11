import sys
from pathlib import Path

# 3rdparty
import s2angs

if len(sys.argv) < 2:
    print('missing args, use .SAFE, .zip or folder containing S2 Data')
    sys.exit()

ang_source = sys.argv[1]
ang_input = Path(f'/mnt/input-dir/{ang_source}')
if Path('/mnt/output-dir/').exists():
    s2angs.gen_s2_ang(str(ang_input), '/mnt/output-dir/')
else:
    s2angs.gen_s2_ang(str(ang_input), '/mnt/input-dir/')