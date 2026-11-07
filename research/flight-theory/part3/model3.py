import numpy as np
m=9000.0; S=28.0; rho=1.225; g=9.81; T_MAX=60000.0
CD0=0.022; K=0.08; CLA=4.8; W=m*g
A_STALL=np.radians(14.0); CL_MAX=CLA*A_STALL      # 1.173
def q(v):return 0.5*rho*v*v
def smooth(x,a,b):t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def cl_linear(a):return CLA*a
def cl_stall(a):
    s=np.sign(a);x=abs(a);d=np.degrees(x)
    if d<=14: c=CLA*x
    elif d<=20: c=CL_MAX+(0.75-CL_MAX)*(d-14)/6
    else: c=0.75*np.cos((min(d,90)-20)/70*np.pi/2)
    return s*c
def cd_of(a,cl,stall=True):
    cd=CD0+K*cl*cl
    if stall: cd+=1.8*np.sin(a)**2*smooth(abs(np.degrees(a)),12,20)
    return cd
def accel(vel,pitch,thrust,clf,stall=True):
    v=np.hypot(*vel);vhat=vel/v;gam=np.arctan2(vel[1],vel[0])
    a=(pitch-gam+np.pi)%(2*np.pi)-np.pi
    cl=clf(a);cd=cd_of(a,cl,stall)
    nose=np.array([np.cos(pitch),np.sin(pitch)]);ldir=np.array([-vhat[1],vhat[0]])
    L=q(v)*S*cl;D=q(v)*S*cd
    F=thrust*nose+L*ldir-D*vhat+np.array([0,-W])
    return F/m,a,L/W
