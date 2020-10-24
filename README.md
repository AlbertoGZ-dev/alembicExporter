# alembicExporter
alembicExporter is a tool to automatize alembic exports for BWater pipeline on demand requests.

<img src=""></img>

## Setup

#### Manual installation

Place the *alembicExporter.py* and *\_\_init\_\_.py* files in a folder named *alembicExporter* in your Maya scripts directory and create a python shell button with the following code:

```python
from alembicExporter import alembicExporter

try:
    md_win.close()
except:
    pass
md_win = alembicExporter.alembicExporter(parent=alembicExporter.getMainWindow())
md_win.show()
md_win.raise_()
```
