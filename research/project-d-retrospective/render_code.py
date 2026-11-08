from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
root=Path(r'F:\Github\Cha-nu')
src=Path(r'F:\EpicGames\Unreal Projects\ProjectD\Source\ProjectD\Private\Weapons\PDRifle.cpp')
lines=src.read_text(encoding='utf-8-sig').splitlines()
font=FontProperties(fname=r'C:\Windows\Fonts\consola.ttf',size=13)
kr=FontProperties(fname=r'C:\Windows\Fonts\NotoSansKR-Regular.ttf',size=18)
fig=plt.figure(figsize=(16,8),facecolor='#171b22'); ax=fig.add_axes([0,0,1,1]);ax.set_axis_off()
ax.text(.04,.94,'메시 트레이스가 실패하면 충돌 지점에서 가까운 본을 찾습니다',fontproperties=kr,color='#ededed')
ax.text(.04,.88,'PDRifle.cpp / RefineCharacterHitToMesh / lines 28–45',fontproperties=font,color='#86bded')
for i,n in enumerate(range(28,46)):
 ax.text(.04,.81-i*.038,f'{n:>2}  '+lines[n-1].replace('\t','    '),fontproperties=font,color='#d8dce2',va='top')
ax.text(.04,.06,'실제 소스 발췌 · 가독성을 위해 이미지로 렌더링 · 실행 화면 아님',fontproperties=FontProperties(fname=r'C:\Windows\Fonts\NotoSansKR-Regular.ttf',size=12),color='#a2a8b2')
out=root/'public/images/devlog/project-d/2026-11-08/02_hit_code.png'
fig.savefig(out,dpi=120,facecolor=fig.get_facecolor());plt.close(fig)