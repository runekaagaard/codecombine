# Basic Import Merging

Tests the basic functionality of combining imports from different files.

Source:

```python
from datetime import datetime, timedelta
from collections import defaultdict
import json
import os.path as osp
```

Destination:

```python
from datetime import datetime
import json
```

Expected Result:

```python
from datetime import datetime, timedelta
import json
from collections import defaultdict
import os.path as osp
```

# Multiple From Imports for Same Module

Tests combining multiple imports from the same module.

Source:

```python
from os.path import join, dirname, basename
from os.path import exists, isfile
from os.path import split as path_split
```

Destination:

```python
from os.path import join, exists
```

Expected Result:

```python
from os.path import join, exists, dirname, basename, isfile, split as path_split
```

# Multiple Source Files

Tests combining imports from multiple source files without duplication.

Source 1:

```python
from typing import List, Dict, Optional
import pandas as pd
```

Source 2:

```python
from typing import Set, Dict, Tuple
import numpy as np
```

Destination:

```python
from typing import List, Set
import pandas as pd
```

Expected Result:

```python
from typing import List, Set, Dict, Optional, Tuple
import pandas as pd
import numpy as np
```

# Handling Import Aliases

Tests correct handling of different alias scenarios.

Source:

```python
from pandas import DataFrame as df, Series as s
import numpy as np
from matplotlib import pyplot as plt
```

Destination:

```python
from pandas import DataFrame as data_frame
import numpy as np
```

Expected Result:

```python
from pandas import DataFrame as data_frame, DataFrame as df, Series as s
import numpy as np
from matplotlib import pyplot as plt
```

# Empty Destination File

Tests adding imports to a file with no existing imports.

Source:

```python
from typing import Optional, List
import sys
from pathlib import Path

def main():
    pass
```

Destination:

```python
def process_data():
    pass
```

Expected Result:

```python
from typing import Optional, List
from pathlib import Path
import sys

def process_data():
    pass
```

# Conditional Imports

Tests handling imports within conditional blocks.

Source:

```python
from typing import Optional
if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict
import json
```

Destination:

```python
from typing import Optional
if sys.version_info >= (3, 8):
    from typing import TypedDict
import yaml
```

Expected Result:

```python
from typing import Optional
import json
if sys.version_info >= (3, 8):
    from typing import TypedDict
import yaml
```

NOTE: Maybe merge if sentences, when we get to symbol combining? If so the Expected Result would be:

<!-- from typing import Optional -->
<!-- if sys.version_info >= (3, 8): -->
<!--     from typing import TypedDict -->
<!-- else: -->
<!--     from typing_extensions import TypedDict -->
<!-- import yaml -->
<!-- import json -->

# Import Comments and Formatting

Tests preservation of comments and formatting around imports.

Source:

```python
# Network related imports
from urllib.parse import urljoin, urlparse
import requests  # HTTP client

# Data processing
import pandas as pd
```

Destination:

```python
# Network related imports
from urllib.parse import urljoin
import requests  # HTTP client
```

Expected Result:

```python
# Network related imports
from urllib.parse import urljoin, urlparse
import requests
import pandas as pd  # HTTP client
```

NOTE: Maybe merge code between imports as well when we get to symbol combining? If so the Expected Result would be:

<!-- # Network related imports -->
<!-- from urllib.parse import urljoin, urlparse -->
<!-- import requests  # HTTP client -->

<!-- # Data processing -->
<!-- import pandas as pd -->

# Relative Imports

Tests handling of relative imports.

Source:

```python
from .utils import helper
from ..base import BaseClass
from ...constants import CONFIG
```

Destination:

```python
from .utils import other_helper
from ..base import BaseClass
```

Expected Result:

```python
from .utils import other_helper, helper
from ..base import BaseClass
from ...constants import CONFIG
```

# Star Imports

Tests handling of star imports and specific imports from the same module.

Source:

```python
from math import *
from math import sqrt, ceil
```

Destination:

```python
from math import floor, ceil
```

Expected Result:

```python
from math import floor, ceil, sqrt
```

# Complex Nested Imports

Tests handling of nested module imports.

Source:

```python
from pkg.subpkg.module import func1, func2
import pkg.subpkg.other as other
from pkg import subpkg
```

Destination:

```python
from pkg.subpkg.module import func1
from pkg import subpkg
```

Expected Result:

```python
from pkg.subpkg.module import func1, func2
from pkg import subpkg
import pkg.subpkg.other as other
```

# Runtime/Dynamic Imports

Tests handling of imports inside functions.

Source:

```python
def load_optional_deps():
    import numpy as np
    from scipy import sparse
    return np, sparse

def main():
    from typing import Optional
    pass
```

Destination:

```python
def load_optional_deps():
    import numpy as np
    return np

def main():
    pass
```

Expected Result:

```python
def load_optional_deps():
    import numpy as np
    from scipy import sparse
    return np, sparse

def main():
    from typing import Optional
    pass
```

# Import Order Dependencies

Tests handling imports with dependencies between them.

Source:

```python
import sys
from pathlib import Path
import os.path as osp
from os.path import join, dirname
```

Destination:

```python
import os.path as osp
from pathlib import Path
```

Expected Result:

```python
import sys
import os.path as osp
from pathlib import Path
from os.path import join, dirname
```

# Type Checking Imports

Tests handling of type checking imports.

Source:

```python
from typing import List, Dict
if TYPE_CHECKING:
    from mypackage.types import MyType
    from other_package import OtherType
```

Destination:

```python
from typing import List
if TYPE_CHECKING:
    from mypackage.types import MyType
```

Expected Result:

```python
from typing import List, Dict
if TYPE_CHECKING:
    from mypackage.types import MyType
    from other_package import OtherType
```

# Circular Import Resolution

Tests handling potential circular imports.

Source:

```python
# circular_a.py
from .b import B
from .c import C
```

Destination:

```python
# circular_b.py
from .a import A
from .c import C
```

Expected Result:

```python
# circular_b.py
from .a import A
from .c import C
from .b import B
```

# Future Imports

Tests handling of future imports which must stay at the top.

Source:

```python
from __future__ import annotations
from __future__ import unicode_literals
import sys
```

Destination:

```python
from __future__ import annotations
import os
```

Expected Result:

```python
from __future__ import annotations
from __future__ import unicode_literals
import os
import sys
```
