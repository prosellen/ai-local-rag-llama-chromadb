from docling.chunking import DocChunk

class CGIDocChunk(DocChunk):
  def __init__(self):
    super().__init__()
    self.id = None
