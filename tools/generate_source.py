"""Generate a native LOS main program from the proven ToolKit shell."""
from pathlib import Path
import json,shutil
R=Path(__file__).resolve().parent
s=(R/'templates/MalomM.TEXT').read_text().replace('program Malom;','program Maze3D;')
s=s.replace('uses (*$U UnitStd.obj *)UnitStd,','uses HWInt, (*$U UnitStd.obj *)UnitStd,')
a=s.index('type BOVideoPtr');b=s.index('   nextClkPoll :')
s=s[:a]+'''type
 MZBoard = packed array[0..224] of char;
 MZPixelBuffer = array[0..6047] of integer;
var
 mzState : array[1..40] of integer;
 mzWorld,mzKeys,mzSeen : MZBoard;
 mzPixels : MZPixelBuffer;
 mzPort : GrafPort;
 mzPortReady,mzViewDirty,mzMapDirty,mzLatchClear : boolean;
 mzHeld,mzEventCount : integer;
 mzNext : longint;
 mzLevelName : Str255;
 mzHud : array[1..3] of Str255;
 mzButtons : integer;
'''+s[b:]
data='procedure MZLoad;\nvar i : integer; row : Str255;\nbegin\ncase mzState[5] of\n'
for k,level in enumerate(json.loads((R.parent/'src/levels.json').read_text())):
 data+=f"{k}:begin\nmzLevelName:='{level['name']}';\n"
 for y,row in enumerate(level['rows']):data+=f"row:='{row}'; for i:=0 to 14 do mzWorld[{y*15}+i]:=row[i+1];\n"
 for x,y in level['keys']:data+=f'mzKeys[{y*15+x}]:=chr(1);\n'
 data+=f"mzState[6]:={level['start'][0]}; mzState[7]:={level['start'][1]}; mzState[8]:={level['facing']};\n"
 data+=f"mzState[9]:={len(level['keys'])}; mzState[10]:={len(level['keys'])}; mzState[19]:={level['exit'][1]*15+level['exit'][0]};\nend;\n"
data+='otherwise\nend\nend;\n'
game=(R.parent/'src/game.pas').read_text().replace('{LEVEL_PROCEDURE}',data)
a=s.index('procedure BlockPresent;');b=s.index('procedure doUpdateEvent',a);s=s[:a]+game+s[b:]
s=s.replace('mmFlags[17] := 0;','mzState[3] := 0;').replace('MMDraw','MZDraw')
s=s.replace('if mmFlags[16]=0 then MMNew;','if mzState[2]=0 then MZInit;')
s=s.replace('FolderSize(myWindow, 500, 260, false);','FolderSize(myWindow, 704, 316, false);\nMoveFolder(myWindow,0,28);')
s=s.replace('MMKey(theEvent.ascii)','MZKey(theEvent.ascii,theEvent.repeatKey)').replace('MMClick;','MZClick;')
s=s.replace('   mmFlags[6] := 0; MMDirty;','   MZRelease;')
s=s.replace('MMInit; mmFlags[16] := 0; mmFlags[2] := 1;','mzState[1] := 24970; mzState[2] := 0; mzPortReady:=false;')
s=s.replace('MMTick;','MZTick;').replace('if myWindow <> nil then BlockPresent;','')
s=s.replace('if EventAvail then begin','mzEventCount:=0;\nwhile EventAvail and (mzEventCount<12) do begin\nmzEventCount:=mzEventCount+1;')
assert 'mmFlags' not in s and 'BlockPresent' not in s
(R.parent/'src/M.TEXT').write_bytes(s.replace('\n','\r').encode('ascii'))
