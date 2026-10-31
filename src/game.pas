procedure MZNum(n : integer; var s : Str255);
begin NumToStr(n,s) end;
function MZAt(x,y : integer) : integer;
begin MZAt:=y*15+x end;
function MZWall(x,y : integer) : boolean;
begin
 MZWall:=true;
 if (x<0) or (x>14) or (y<0) or (y>14) then exit(MZWall);
 MZWall:=mzWorld[MZAt(x,y)]='#'
end;
procedure MZDelta(d : integer; var dx,dy : integer);
begin
 dx:=0; dy:=0;
 case d of 0:dy:=-1; 1:dx:=1; 2:dy:=1; 3:dx:=-1; otherwise end
end;
procedure MZReveal;
var x,y,d,dx,dy : integer;
begin
 x:=mzState[6]; y:=mzState[7]; mzSeen[MZAt(x,y)]:=chr(1);
 for d:=0 to 3 do begin
  MZDelta(d,dx,dy);
  if (x+dx>=0) and (x+dx<15) and (y+dy>=0) and (y+dy<15) then
   mzSeen[MZAt(x+dx,y+dy)]:=chr(1)
 end
end;
procedure MZReport;
var p,n,s : integer;
begin
 n:=0; s:=0;
 for p:=0 to 224 do begin
  n:=n+ord(mzSeen[p]);
  if (ord(mzKeys[p])<>0) or (ord(mzSeen[p])<>0) then
   s:=(longint(s)+longint(p+1)*(ord(mzKeys[p])+ord(mzSeen[p]))) mod 30011
 end;
 mzState[22]:=n; mzState[26]:=s; mzState[27]:=ord(mzLatchClear);
 mzState[21]:=(mzState[21]+1) mod 30000
end;
{LEVEL_PROCEDURE}
procedure MZReset;
var i : integer;
begin
 mzState[20]:=1;
 for i:=0 to 224 do begin mzWorld[i]:='#'; mzKeys[i]:=chr(0); mzSeen[i]:=chr(0) end;
 mzState[4]:=1; mzState[11]:=0; mzState[12]:=0; mzState[13]:=0; mzState[14]:=0;
 mzState[15]:=0; mzState[16]:=0; mzState[17]:=1; mzState[3]:=0;
 MZLoad; MZReveal; mzHeld:=0; mzLatchClear:=true; mzNext:=Timer;
 mzViewDirty:=true; mzMapDirty:=true; MZReport; mzState[20]:=0
end;
procedure MZAction(a : integer);
var dx,dy,x,y,p : integer;
begin
 if mzState[4]<>1 then exit(MZAction);
 mzState[20]:=1; mzState[16]:=a; mzState[11]:=(mzState[11]+1) mod 30000;
 if (a=1) or (a=2) then begin
  if a=1 then mzState[8]:=(mzState[8]+3) mod 4 else mzState[8]:=(mzState[8]+1) mod 4;
  mzState[13]:=(mzState[13]+1) mod 30000; mzViewDirty:=true; mzMapDirty:=true
 end else begin
  MZDelta(mzState[8],dx,dy);
  if a=4 then begin dx:=-dx; dy:=-dy end;
  x:=mzState[6]+dx; y:=mzState[7]+dy;
  if MZWall(x,y) then mzState[14]:=(mzState[14]+1) mod 30000
  else begin
   mzState[6]:=x; mzState[7]:=y; mzState[12]:=(mzState[12]+1) mod 30000;
   p:=MZAt(x,y);
   if ord(mzKeys[p])<>0 then begin mzKeys[p]:=chr(0); mzState[9]:=mzState[9]-1 end;
   MZReveal;
   if (p=mzState[19]) and (mzState[9]=0) then mzState[4]:=2;
   mzViewDirty:=true; mzMapDirty:=true
  end
 end;
 MZReport; mzState[20]:=0
end;
function MZLeft(d : integer) : integer;
begin
 case d of 0:MZLeft:=0; 1:MZLeft:=96; 2:MZLeft:=148;
  3:MZLeft:=176; 4:MZLeft:=194; otherwise MZLeft:=205 end
end;
function MZTop(d : integer) : integer;
begin
 case d of 0:MZTop:=0; 1:MZTop:=42; 2:MZTop:=66;
  3:MZTop:=80; 4:MZTop:=88; otherwise MZTop:=95 end
end;
procedure MZQuad(x0,y0,x1,y1,x2,y2,x3,y3,shade : integer);
var xs,ys : array[0..4] of integer;
    i,j,y,lo,hi,l,r,z,a,b,deltaX,deltaY,denom,tmp : integer;
    work : longint;
begin
 xs[0]:=x0; xs[1]:=x1; xs[2]:=x2; xs[3]:=x3; xs[4]:=x0;
 ys[0]:=y0; ys[1]:=y1; ys[2]:=y2; ys[3]:=y3; ys[4]:=y0;
 lo:=y0; hi:=y0;
 for i:=1 to 3 do begin if ys[i]<lo then lo:=ys[i]; if ys[i]>hi then hi:=ys[i] end;
 for y:=lo to hi do if ((y+shade) mod 4)=0 then begin
  l:=448; r:=-1;
  for i:=0 to 3 do begin
   j:=i+1; a:=ys[i]; b:=ys[j];
   if a>b then begin tmp:=a; a:=b; b:=tmp end;
   if (a<=y) and (y<b) then begin
    deltaX:=xs[j]-xs[i]; deltaY:=y-ys[i]; denom:=ys[j]-ys[i];
    work:=longint(deltaY)*longint(deltaX); work:=work div denom;
    z:=work; z:=xs[i]+z;
    if z<l then l:=z; if z>r then r:=z
   end
  end;
  if l<=r then begin MoveTo(l,y); LineTo(r,y) end
 end;
 MoveTo(x0,y0); LineTo(x1,y1); LineTo(x2,y2); LineTo(x3,y3); LineTo(x0,y0)
end;
procedure MZFront(d : integer);
var l,t,r,b,y,x,w,h : integer; box : Rect;
begin
 l:=MZLeft(d); t:=MZTop(d); r:=448-l; b:=216-t;
 SetRect(box,l,t,r,b); FrameRect(box);
 h:=(b-t) div 4; if h<5 then h:=5;
 y:=t+h;
 while y<b do begin
  MoveTo(l,y); LineTo(r-1,y); w:=(r-l) div 4; if w<8 then w:=8;
  x:=l+w div 2;
  if ((y-t) div h mod 2)=0 then x:=l+w;
  while x<r do begin MoveTo(x,y-h); LineTo(x,y); x:=x+w end;
  y:=y+h
 end
end;
procedure MZView;
var d,depth,dx,dy,lx,ly,x,y,l,t,nl,nt,r,b,nr,nb,p,w,h,k : integer;
    box,src,dst : Rect;
begin
 SetPort(@mzPort); SetRect(box,0,0,448,216); ClipRect(box); EraseRect(box); PenSize(1,1);
 MZDelta(mzState[8],dx,dy); MZDelta((mzState[8]+3) mod 4,lx,ly);
 depth:=5;
 for d:=1 to 5 do if depth=5 then begin
  x:=mzState[6]+dx*d; y:=mzState[7]+dy*d;
  if MZWall(x,y) then depth:=d
 end;
 x:=mzState[6]+dx*depth; y:=mzState[7]+dy*depth;
 if MZWall(x,y) then MZFront(depth)
 else begin SetRect(box,205,95,243,121); PaintRect(box) end;
 for d:=depth-1 downto 0 do begin
  x:=mzState[6]+dx*d; y:=mzState[7]+dy*d;
  l:=MZLeft(d); t:=MZTop(d); r:=448-l; b:=216-t;
  nl:=MZLeft(d+1); nt:=MZTop(d+1); nr:=448-nl; nb:=216-nt;
  if MZWall(x+lx,y+ly) then MZQuad(l,t,nl,nt,nl,nb,l,b,0)
  else begin
   MoveTo(l,nt); LineTo(nl,nt); MoveTo(l,nb); LineTo(nl,nb);
   MoveTo(l,nt); LineTo(l,nb); MoveTo(nl,nt); LineTo(nl,nb)
  end;
  if MZWall(x-lx,y-ly) then MZQuad(nr,nt,r,t,r,b,nr,nb,2)
  else begin
   MoveTo(nr,nt); LineTo(r,nt); MoveTo(nr,nb); LineTo(r,nb);
   MoveTo(nr,nt); LineTo(nr,nb); MoveTo(r,nt); LineTo(r,nb)
  end;
  MoveTo(nl,nb); LineTo(nr,nb);
  MoveTo(l,b); LineTo(nl,nb); MoveTo(r,b); LineTo(nr,nb);
  p:=MZAt(x,y); w:=(nr-nl) div 8; if w<2 then w:=2;
  if p=mzState[19] then begin
   h:=(nb-nt)*3 div 4; SetRect(box,224-w*2,nb-h,224+w*2,nb); FrameRect(box);
   MoveTo(224-w*2,nb-h); LineTo(224+w*2,nb);
   if mzState[9]>0 then begin
    MoveTo(224,nb-h); LineTo(224,nb); MoveTo(224-w*2,nb); LineTo(224+w*2,nb-h)
   end
  end;
  if ord(mzKeys[p])<>0 then begin
   k:=nb-w; MoveTo(224,k-w); LineTo(224+w,k); LineTo(224,k+w); LineTo(224-w,k); LineTo(224,k-w);
   MoveTo(224,k-w div 2); LineTo(224,k+w div 2)
  end
 end;
 SetRect(box,0,0,448,216); FrameRect(box);
 SetPort(myWindow); ClipRect(myWindow^.portRect);
 SetRect(src,0,0,448,216); SetRect(dst,16,40,464,256);
 CopyBits(mzPort.portBits,myWindow^.portBits,src,dst,srcCopy,nil)
end;
procedure MZMap;
var p,x,y,d,dx,dy,cx,cy,tx,ty : integer; box,src,dst : Rect;
begin
 SetPort(@mzPort); SetRect(box,0,0,448,216); ClipRect(box);
 SetRect(box,0,0,180,180); EraseRect(box); PenSize(1,1);
 for p:=0 to 224 do begin
  x:=(p mod 15)*12; y:=(p div 15)*12;
  if (mzState[17]=1) or (ord(mzSeen[p])<>0) then begin
   if mzWorld[p]='#' then begin SetRect(box,x+1,y+1,x+11,y+11); PaintRect(box) end;
   if ord(mzKeys[p])<>0 then begin
    MoveTo(x+6,y+3); LineTo(x+9,y+6); LineTo(x+6,y+9); LineTo(x+3,y+6); LineTo(x+6,y+3)
   end;
   if p=mzState[19] then begin
    SetRect(box,x+2,y+2,x+10,y+10); FrameRect(box);
    if mzState[9]>0 then begin MoveTo(x+5,y+2); LineTo(x+5,y+9); MoveTo(x+7,y+2); LineTo(x+7,y+9) end
   end
  end else begin
   SetRect(box,x+3,y+3,x+5,y+5); PaintRect(box); SetRect(box,x+8,y+8,x+10,y+10); PaintRect(box)
  end
 end;
 x:=mzState[6]*12; y:=mzState[7]*12; cx:=x+6; cy:=y+6; MZDelta(mzState[8],dx,dy);
 SetRect(box,x+5,y+5,x+8,y+8); PaintRect(box);
 tx:=cx+dx*8; ty:=cy+dy*8;
 MoveTo(cx,cy); LineTo(tx,ty); MoveTo(tx,ty);
 tx:=cx+dx*4; tx:=tx+dy*3; ty:=cy+dy*4; ty:=ty-dx*3; LineTo(tx,ty);
 tx:=cx+dx*8; ty:=cy+dy*8; MoveTo(tx,ty);
 tx:=cx+dx*4; tx:=tx-dy*3; ty:=cy+dy*4; ty:=ty+dx*3; LineTo(tx,ty);
 SetPort(myWindow); ClipRect(myWindow^.portRect);
 SetRect(src,0,0,180,180); SetRect(dst,490,52,670,232);
 CopyBits(mzPort.portBits,myWindow^.portBits,src,dst,srcCopy,nil)
end;
procedure MZHudLine(line : integer; s : Str255);
var r : Rect;
begin
 if s=mzHud[line] then exit(MZHudLine);
 case line of
  1:begin SetRect(r,8,0,698,18); EraseRect(r); MoveTo(12,14) end;
  2:begin SetRect(r,8,18,698,36); EraseRect(r); MoveTo(12,29) end;
  3:begin SetRect(r,8,298,698,316); EraseRect(r); MoveTo(12,311) end;
  otherwise
 end;
 DrawString(s); mzHud[line]:=s
end;
procedure MZDraw;
var r : Rect; i,p : integer; s,t,u,v : Str255;
begin
 if myWindow=nil then exit(MZDraw);
 mzState[20]:=1;
 SetPort(myWindow); ClipRect(myWindow^.portRect); TextFont(0); TextSize(12); PenSize(1,1);
 if not mzPortReady then begin
  OpenPort(@mzPort); SetRect(mzPort.portRect,0,0,448,216);
  mzPort.portBits.baseAddr:=QDPtr(@mzPixels); mzPort.portBits.rowBytes:=56;
  mzPort.portBits.bounds:=mzPort.portRect; mzPortReady:=true; SetPort(myWindow)
 end;
 if mzState[3]=0 then begin
  SetRect(r,0,0,704,316); EraseRect(r);
  for i:=1 to 3 do mzHud[i]:=''; mzButtons:=-1;
  MoveTo(490,46); DrawString('TERKEP'); MoveTo(490,245); DrawString('Kulcs: rombusz  Kapu: X');
  mzViewDirty:=true; mzMapDirty:=true
 end;
 if mzViewDirty then begin MZView; mzViewDirty:=false end;
 if mzMapDirty then begin MZMap; mzMapDirty:=false end;
 SetPort(myWindow); TextFont(0); TextSize(12);
 MZNum(mzState[5]+1,t); MZNum(mzState[9],u); MZNum(mzState[12],v);
 s:=concat('LABIRINTUS 3D  ',t,'/3: ',mzLevelName);
 s:=concat(s,'    Kulcs: ',u,'    Lepes: ',v); MZHudLine(1,s);
 if mzState[4]=2 then s:='KIJUTOTTAL! Minden kulcs megvan. Kovetkezo palya: uj kaland.'
 else if (MZAt(mzState[6],mzState[7])=mzState[19]) and (mzState[9]>0) then
  s:='A KIJARAT ZARVA. Gyujtsd ossze az osszes kulcsot, aztan terj vissza!'
 else s:='Gyujtsd ossze a kulcsokat! A kijaratot a terkepen X jeloli.';
 MZHudLine(2,s);
 case mzState[8] of 0:t:='ESZAK'; 1:t:='KELET'; 2:t:='DEL'; 3:t:='NYUGAT'; otherwise t:='' end;
 s:=concat('Bal/Jobb: fordulas. Fel: elore. Le: hatra. Irany: ',t); MZHudLine(3,s);
 p:=mzState[17];
 if mzButtons<>p then begin
  for i:=0 to 3 do begin
   SetRect(r,16+i*172,272,176+i*172,294); EraseRect(r); FrameRect(r); MoveTo(23+i*172,287);
   case i of
    0:DrawString('Ujra'); 1:DrawString('Elozo palya'); 2:DrawString('Kovetkezo palya');
    3:if p=1 then DrawString('Terkep: teljes') else DrawString('Terkep: felfedes'); otherwise
   end
  end; mzButtons:=p
 end;
 mzState[3]:=1; mzState[18]:=(mzState[18]+1) mod 30000;
 MZReport; mzState[20]:=0
end;
procedure MZKey(ch : char; repeated : boolean);
begin
 { Arrow key state is polled. Character repeat never drives movement. }
end;
procedure MZRelease;
begin
 mzHeld:=0; mzState[15]:=0; mzLatchClear:=true; MZReport
end;
procedure MZClick;
var pt : Point; b : integer;
begin
 SetPort(myWindow); GetMouse(pt);
 if (pt.v<272) or (pt.v>=294) or (pt.h<16) or (pt.h>=692) then exit(MZClick);
 b:=(pt.h-16) div 172;
 if ((pt.h-16) mod 172)>=160 then exit(MZClick);
 case b of
  0:MZReset;
  1:begin mzState[5]:=(mzState[5]+2) mod 3; MZReset end;
  2:begin mzState[5]:=(mzState[5]+1) mod 3; MZReset end;
  3:begin mzState[17]:=1-mzState[17]; mzMapDirty:=true; MZRelease end;
  otherwise
 end;
 MZDraw
end;
procedure MZInit;
var i : integer;
begin
 for i:=1 to 40 do mzState[i]:=0;
 mzState[1]:=24970; mzState[2]:=1; mzState[5]:=0; mzPortReady:=false;
 mzState[23]:=ord(@mzWorld)-ord(@mzState); mzState[24]:=ord(@mzKeys)-ord(@mzState);
 mzState[25]:=ord(@mzSeen)-ord(@mzState); MZReset
end;
procedure MZTick;
var keys : KeySet; mask,a : integer; changed : boolean;
begin
 if (myWindow=nil) or (activeFolder<>myWindow) then exit(MZTick);
 GetKeys(keys); mask:=0;
 if 34 in keys then mask:=mask+1; if 35 in keys then mask:=mask+2;
 if 39 in keys then mask:=mask+4; if 43 in keys then mask:=mask+8;
 changed:=mask<>mzState[15]; mzState[15]:=mask;
 if changed then MZReport;
 if mzLatchClear then begin
  if mask=0 then begin mzLatchClear:=false; MZReport end;
  exit(MZTick)
 end;
 if mzState[4]<>1 then exit(MZTick);
 a:=0; case mask of 1:a:=1; 2:a:=2; 4:a:=3; 8:a:=4; otherwise end;
 if a=0 then begin mzHeld:=0; exit(MZTick) end;
 if (a<>mzHeld) or (Timer>=mzNext) then begin
  mzHeld:=a; mzNext:=Timer+180; MZAction(a); MZDraw
 end
end;
