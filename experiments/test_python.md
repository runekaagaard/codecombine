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
