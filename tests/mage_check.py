from pathlib import Path
from lupa.lua51 import LuaRuntime
root=Path(__file__).resolve().parents[1]
source=(root/'MageToolkit.lua').read_text(encoding='utf-8-sig')
def setup():
    lua=LuaRuntime(unpack_returned_tuples=True)
    lua.execute('''
    SlashCmdList={}; WaterTradeForeverDB={enabled=false,classOffers={MAGE='both'}}
    macros={}; calls=0; combat=false; class='MAGE'; MAX_ACCOUNT_MACROS=120; MAX_CHARACTER_MACROS=18
    function InCombatLockdown() return combat end
    function UnitClass() return class,class end
    C_Spell={GetSpellName=function(id) return 'Spell'..id end}
    function GetNumMacros() return accounts or 0,characters or 0 end
    function GetMacroInfo(i) if macros[i] then return macros[i][1],134400,macros[i][2] end end
    function CreateMacro(name,icon,body,character)
      calls=calls+1; lastScope=character
      if reject then error('blocked') end
      local id=character and 121 or 1; macros[id]={name,truncate and body:sub(1,10) or body}; return id
    end
    widgets={}; UISpecialFrames={}; UIParent={}; ChatFontNormal={}
    function CreateFrame(kind,name,parent,template)
      local w={scripts={},text={SetText=function() end},TitleText={SetText=function() end}}
      setmetatable(w,{__index=function(_,key) return function() end end})
      function w:SetScript(key,fn) self.scripts[key]=fn end
      function w:SetText(text) self.value=text end
      function w:SetChecked(v) self.checked=v end
      function w:GetChecked() return self.checked end
      function w:CreateFontString() return CreateFrame('Font') end
      widgets[#widgets+1]=w
      return w
    end
    function UIDropDownMenu_SetWidth() end
    function UIDropDownMenu_SetText(w,text) w.selected=text end
    function UIDropDownMenu_Initialize(w,fn) w.initialize=fn end
    function UIDropDownMenu_CreateInfo() return {} end
    function UIDropDownMenu_AddButton(info) entries[#entries+1]=info end
    C_Item={GetItemCount=function(id,bank) assert(not bank); return 2 end}
    function WaterboyOpenTradeSettings() tradeOpened=true end
    ''')
    lua.execute(source)
    return lua
cases=[
 ('character create', '', 'ok and calls==1 and lastScope==true'),
 ('account create', 'WaterboyMage.Build(1); WaterTradeForeverDB.mage.character=false', 'ok and calls==1 and lastScope==false'),
 ('combat', 'combat=true','not ok and calls==0'),
 ('non mage', "class='ROGUE'",'not ok and calls==0'),
 ('account collision', "macros[1]={'WB Counterspell','custom'}",'not ok and calls==0 and macros[1][2]=="custom"'),
 ('character collision', "macros[121]={'WB Counterspell','custom'}",'not ok and calls==0'),
 ('full character', 'characters=18','not ok and calls==0'),
 ('full account', 'WaterboyMage.Build(1); WaterTradeForeverDB.mage.character=false; accounts=120','not ok and calls==0'),
 ('missing api', 'CreateMacro=nil','not ok and calls==0'),
 ('missing spell', 'C_Spell.GetSpellName=function() end','not ok and calls==0'),
 ('too long localized name', "C_Spell.GetSpellName=function() return string.rep('x',130) end",'not ok and calls==0'),
 ('client rejects', 'reject=true','not ok and calls==1'),
 ('readback mismatch', 'truncate=true','not ok and calls==1'),
]
for name,before,expected in cases:
    lua=setup(); lua.execute(before+'\n ok,msg=WaterboyMage.Create(1); assert('+expected+')'); print('PASS',name)
lua=setup()
lua.execute('''
for i,t in ipairs(WaterboyMage.templates) do
 local body=WaterboyMage.Build(i); assert(#body<=255 and #('WB '..t[1])<=16)
 assert(not body:find('/run') and not body:find('/script'))
end
WaterTradeForeverDB.mage.enemy='focus'; assert(WaterboyMage.Build(1):find('[@focus,harm,nodead][]',1,true))
WaterTradeForeverDB.mage.enemy='mouseover'; assert(WaterboyMage.Build(2):find('[@mouseover,harm,nodead][]',1,true))
WaterTradeForeverDB.mage.stopcast=false; assert(not WaterboyMage.Build(1):find('/stopcasting',1,true))
WaterTradeForeverDB.mage.mouseover=true; assert(WaterboyMage.Build(3):find('[@mouseover,help,nodead]',1,true))
assert(WaterboyMage.Build(7):find('/cancelaura',1,true)); assert(WaterboyMage.Build(6):find('/cancelaura Spell11958',1,true))
assert(WaterTradeForeverDB.enabled==false and WaterTradeForeverDB.classOffers.MAGE=='both')
WaterboyMage.Open()
local count=#widgets
WaterboyMage.Open(); assert(#widgets==count)
for _,w in ipairs(widgets) do
 if rawget(w,"initialize") then entries={}; w.initialize(); assert(#entries==34); entries[2].func() end
end
for _,w in ipairs(widgets) do
 if w.value=='Create macro' then w.scripts.OnClick() end
end
assert(macros[121][1]=='WB Polymorph')
''')
print('PASS template limits, targeting, Ice Block cancellation, settings preservation and window callbacks')
# Load modules in their actual order, then exercise the slash entry point.
lua=setup(); lua.execute((root/'WaterboyForever.lua').read_text()); lua.execute(source)
lua.execute("SlashCmdList.WATERTRADEFOREVER(''); assert(WaterboyMage)")
print('PASS combined module load and slash routing')


# Cancellation must precede casting: putting it after would remove the new block.
lua=setup()
build=lua.globals().WaterboyMage.Build
block=build(6)
assert block.index('/stopcasting') < block.index('/cancelaura') < block.index('/cast ')
assert '/cast [nochanneling] ' in build(10)
assert '/stopattack' in build(2)
assert '[mod:shift][btn:2]' in build(19)
assert '/cast [@cursor]' in build(20)
assert '/cast !' in build(21)
assert '/cancelaura [mod:shift]' in build(22) and '/cast [nomod:shift,@player]' in build(22)
for i in (8,9):
    assert build(i).index('/cancelaura') < build(i).index('/cast ')
print('PASS cancellation ordering, escape macros, channel protection and utility modifiers')
