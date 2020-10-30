# write a short python script to parse out the cell notation blocks and substitute them for empty strings
import re #python regular expression matching module
script = re.sub(r'# In\[.*\]:\n','',open('missionMars_ra.py').read())
with open('scrapeMars_ra.py','w') as fh:
    fh.write(script)