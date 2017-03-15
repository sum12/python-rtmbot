[cron](../../lib.py)
-------------------

Every plugin can now provide its own cron config in rtmbot.conf file. 
Check [example-config](../example-config/rtmbot.conf).

Try not to write very complicated cronstring as the implementation is in
experimental phase.


```python
from lib import *

# schfun.next() should give the number of seconds to wait before the
# next execution.
schfunc = cronfromstring('* * * * *')

#this will print the subsequent execution times.
print datetime.now() + timedelta(seconds=schfunc.next())
```
