import numpy as np
# 단순화한 2D(세로면) 점질량 모델: x 수평, z 위
m=9000.0; S=28.0; rho=1.225; g=9.81; T_MAX=60000.0
CD0=0.022; K=0.08; CLA=4.8   # CLA: 1/rad
W=m*g
def q(v):return 0.5*rho*v*v
def forces(vel,pitch,thrust,lift_mode="aoa",cl_fixed=None):
    """vel: (vx,vz), pitch: 기수 각도(rad). 반환: 가속도"""
    v=np.hypot(*vel); vhat=vel/v; gamma=np.arctan2(vel[1],vel[0])
    nose=np.array([np.cos(pitch),np.sin(pitch)]); up_body=np.array([-np.sin(pitch),np.cos(pitch)])
    lift_dir=np.array([-vhat[1],vhat[0]])            # 속도에 수직
    if lift_mode=="aoa":
        a=pitch-gamma; cl=CLA*a; L=q(v)*S*cl; Ldir=lift_dir
    else:                                             # 고정 계수, 기체 위 방향
        cl=cl_fixed; L=q(v)*S*cl; Ldir=up_body
    D=q(v)*S*(CD0+K*cl*cl)
    F=thrust*nose + L*Ldir - D*vhat + np.array([0,-W])
    return F/m
def step(p,v,a,dt,method):
    if method=="explicit": return p+v*dt, v+a*dt
    v2=v+a*dt; return p+v2*dt, v2                   # 반암시적(semi-implicit) 오일러
