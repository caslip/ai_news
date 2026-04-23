"""Fix nitter source username in database"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import engine
from app.models.source import Source

db = Session(bind=engine)
try:
    # 直接修改 ORM 对象
    sources = db.query(Source).filter(Source.type == 'netter').all()
    print(f'Nitter sources found: {len(sources)}')
    for s in sources:
        print(f'  Before: name={s.name}, config={s.config}')
        s.config = {"username": "Khazix0918"}
        print(f'  After:  name={s.name}, config={s.config}')

    db.commit()
    print('\nCommit successful!')

    # 最终验证
    sources = db.query(Source).all()
    for s in sources:
        t = s.type.value if hasattr(s.type, 'value') else s.type
        print(f'Final: name={s.name}, type={t}, config={s.config}')
finally:
    db.close()
