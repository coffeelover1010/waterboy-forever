from pathlib import Path
from lupa.lua51 import LuaRuntime

source = (Path(__file__).resolve().parents[1] / 'WaterboyForever.lua').read_text()
def setup():
    lua = LuaRuntime()
    lua.execute('''
    SlashCmdList = {}; NUM_BAG_SLOTS = 0; timers = {}; offered = 0; trades = {}; quantities = {}; moves = 0
    class = 'MAGE'; level = 30; visible = true; combat = false
    bags = {{itemID=5350, stackCount=20}, {itemID=3772, stackCount=20}}
    frame = {RegisterEvent=function() end, SetScript=function(self, _, f) self.event=f end}
    function CreateFrame() return frame end
    function print() end
    function InCombatLockdown() return combat end
    function UnitIsPlayer() return true end
    function UnitClass() return class, class end
    function UnitLevel() return level end
    function GetCursorInfo() if cursor then return 'item',cursor end end
    function ClearCursor()
      if cursor and origin then
        local old=bags[origin]
        if old then old.stackCount=old.stackCount+cursorCount
        else bags[origin]={itemID=cursor,stackCount=cursorCount} end
      end
      cursor=nil; cursorCount=nil
    end
    function GetTradePlayerItemInfo(slot) if slot==1 then return trade end end
    function ClickTradeButton(slot) offered=offered+1; trades[slot]=cursor; quantities[slot]=cursorCount; trade=cursor; cursor=nil; cursorCount=nil end
    TradeFrame = {IsShown=function() return visible end}
    C_Timer = {After=function(_, f) timers[#timers+1]=f end}
    C_Container = {
      GetContainerNumSlots=function() return #bags end,
      GetContainerItemInfo=function(_, slot) return bags[slot] end,
      PickupContainerItem=function(_, slot)
        local item=bags[slot]
        if cursor then
          assert(item and item.itemID==cursor and item.stackCount+cursorCount<=20)
          item.stackCount=item.stackCount+cursorCount; cursor=nil; cursorCount=nil; moves=moves+1
        else
          cursor=item.itemID; cursorCount=item.stackCount; origin=slot; bags[slot]=false
        end
      end,
      SplitContainerItem=function(_,slot,count)
        local item=bags[slot]; assert(count<item.stackCount)
        cursor=item.itemID; cursorCount=count; origin=slot; item.stackCount=item.stackCount-count
      end
    }
    C_Item = {GetItemInfo=function(id)
      return 'water','link',1,1,((id==3772 or id==1487) and 25 or 1),nil,nil,20
    end, RequestLoadItemDataByID=function() end}
    function event(e,a,b) frame.event(frame,e,a,b) end
    function flush() local t=timers; timers={}; for _,f in ipairs(t) do f() end end
    ''')
    lua.execute(source)
    lua.execute("event('ADDON_LOADED','WaterboyForever')")
    return lua

cases = [
    ('best rank and once', '', 'offered==1 and trade==3772'),
    ('lower level', 'level=10', 'offered==1 and trade==5350'),
    ('warrior', "class='WARRIOR'", 'offered==0'),
    ('hunter both', "class='HUNTER'; bags[3]={itemID=1113, stackCount=20}", 'offered==2 and trades[1]==3772 and trades[2]==1113'),
    ('warrior food', "class='WARRIOR'; bags[3]={itemID=1113, stackCount=20}", 'offered==1 and trades[1]==1113'),
    ('hunter food alone', "class='HUNTER'; bags={{itemID=1113, stackCount=20}}", 'offered==1 and trades[1]==1113'),
    ('rogue food only', "class='ROGUE'; bags[3]={itemID=1113, stackCount=20}", 'offered==1 and trades[1]==1113'),
    ('rogue no food', "class='ROGUE'", 'offered==0'),
    ('rogue partial food', "class='ROGUE'; bags[3]={itemID=1113, stackCount=19}", 'offered==1 and quantities[1]==19'),
    ('rogue prefers better partial', "class='ROGUE'; bags={{itemID=1113,stackCount=20},{itemID=1487,stackCount=7}}", 'trade==1487 and quantities[1]==7'),
    ('rogue combines remainder', "class='ROGUE'; bags={{itemID=1487,stackCount=7},{itemID=1487,stackCount=8}}", 'offered==1 and quantities[1]==15 and moves==1'),
    ('rogue caps combined stack', "class='ROGUE'; bags={{itemID=1487,stackCount=12},{itemID=1487,stackCount=12}}", 'offered==1 and quantities[1]==20 and bags[2].stackCount==4'),
    ('rogue level restriction', "class='ROGUE'; level=10; bags={{itemID=1113,stackCount=6},{itemID=1487,stackCount=20}}", 'trade==1113 and quantities[1]==6'),
    ('hunter combines both', "class='HUNTER'; bags={{itemID=3772,stackCount=7},{itemID=3772,stackCount=8},{itemID=1487,stackCount=3},{itemID=1487,stackCount=4}}", 'offered==2 and quantities[1]==15 and quantities[2]==7'),
    ('bound bread skipped', "class='ROGUE'; bags={{itemID=1487,stackCount=10,isBound=true}}", 'offered==0'),
    ('shapeshifted druid', "class='DRUID'", 'offered==1'),
    ('partial stacks', 'bags[1].stackCount=19; bags[2].stackCount=5', 'offered==1 and trade==3772 and quantities[1]==5'),
    ('populated trade', 'trade=123', 'offered==0 and trade==123'),
    ('busy cursor', 'cursor=123', 'offered==0 and cursor==123'),
    ('combat', 'combat=true', 'offered==0'),
    ('disabled', 'WaterTradeForeverDB.enabled=false', 'offered==0'),
    ('locked bags', 'bags[2].isLocked=true', 'offered==0'),
]
for label, before, assertion in cases:
    lua = setup()
    lua.execute(before + "\n event('TRADE_SHOW'); flush(); assert(" + assertion + ")")
    print('PASS', label)
lua = setup()
lua.execute("event('TRADE_SHOW'); event('TRADE_CLOSED'); flush(); assert(offered==0)")
lua.execute("event('TRADE_SHOW'); timers[1](); trade=nil; flush(); assert(offered==1)")
lua.execute("event('TRADE_CLOSED'); event('TRADE_SHOW'); flush(); assert(offered==2)")
print('PASS cancellation, removal and next trade')
lua = setup()
lua.execute("event('TRADE_SHOW'); event('TRADE_ACCEPT_UPDATE',1,0); flush(); assert(offered==0)")
print('PASS accepted trade remains untouched')

for stop in ("event('TRADE_CLOSED')", "event('TRADE_ACCEPT_UPDATE',1,0)", "combat=true", "trade=123"):
    lua=setup()
    lua.execute("class='ROGUE'; bags={{itemID=1487,stackCount=7},{itemID=1487,stackCount=8}}; event('TRADE_SHOW'); timers[1](); assert(moves==1 and offered==0)")
    lua.execute(stop + "; flush(); assert(offered==0)")
print('PASS consolidation stops on closure, acceptance, combat and manual trade items')
lua=setup()
lua.execute("class='ROGUE'; bags={}; for i=1,20 do bags[i]={itemID=1487,stackCount=1} end; event('TRADE_SHOW'); flush(); assert(offered==1 and quantities[1]==20)")
print('PASS twenty single breads consolidate into one offer')

# Acceptance occurs only when the user invokes the binding.
import xml.etree.ElementTree as ET
binding = ET.parse(Path(__file__).resolve().parents[1] / 'Bindings.xml').getroot().find('Binding')
assert binding.attrib['name'] == 'WATERBOY_ACCEPT_TRADE'
lua=setup()
lua.execute("accepts=0; buttonEnabled=true; function AcceptTrade() accepts=accepts+1 end; TradeFrameTradeButton={IsEnabled=function() return buttonEnabled end}")
lua.execute("event('TRADE_SHOW'); flush(); flush(); event('TRADE_ACCEPT_UPDATE',0,1); assert(accepts==0)")
lua.execute(binding.text)
lua.execute("assert(accepts==1); visible=false")
lua.execute(binding.text)
lua.execute("assert(accepts==1); visible=true; buttonEnabled=false")
lua.execute(binding.text)
lua.execute("assert(accepts==1)")
print('PASS binding accepts only on invocation with visible trade and enabled button; no automatic acceptance')

# Class defaults and saved overrides drive actual trade contents.
for cls, mode in {'WARRIOR':'food','PALADIN':'water','HUNTER':'both','ROGUE':'food','PRIEST':'water','SHAMAN':'water','MAGE':'water','WARLOCK':'both','DRUID':'water'}.items():
    for override in [None, 'food', 'water', 'both', 'invalid']:
        lua=setup()
        selected=override if override in ('food','water','both') else mode
        lua.globals().class_token=cls
        lua.execute("class=class_token; bags={{itemID=3772,stackCount=8},{itemID=1487,stackCount=7}}")
        if override:
            lua.globals().override=override
            lua.execute("WaterTradeForeverDB.classOffers[class]=override")
        lua.execute("event('TRADE_SHOW'); flush()")
        expected={'food':[1487], 'water':[3772], 'both':[3772,1487]}[selected]
        assert lua.globals().offered == len(expected), (cls, override)
        assert [lua.globals().trades[i+1] for i in range(len(expected))] == expected
print('PASS all nine class defaults, all override modes and invalid-value fallback')

lua=setup()
lua.execute("""
widgets={}; UISpecialFrames={}; UIParent={}
function CreateFrame(kind,name,parent,template)
    local w={scripts={}, text={SetText=function() end}, TitleText={SetText=function() end}}
    setmetatable(w,{__index=function(_,key) return function() end end})
    function w:SetScript(key,fn) self.scripts[key]=fn end
    function w:SetChecked(value) self.checked=value end
    function w:GetChecked() return self.checked end
    function w:CreateFontString() return {SetPoint=function() end,SetText=function() end} end
    widgets[#widgets+1]=w
    return w
end
function UIDropDownMenu_SetWidth() end
function UIDropDownMenu_SetText(w,text) w.selected=text end
function UIDropDownMenu_Initialize(w,fn) w.initialize=fn end
function UIDropDownMenu_CreateInfo() return {} end
function UIDropDownMenu_AddButton(info) entries[#entries+1]=info end
SlashCmdList.WATERTRADEFOREVER('')
assert(#widgets==12)
local classes={'WARRIOR','PALADIN','HUNTER','ROGUE','PRIEST','SHAMAN','MAGE','WARLOCK','DRUID'}
for i,class in ipairs(classes) do
    local dropdown=widgets[i+2]
    entries={}; dropdown.initialize()
    assert(#entries==3)
    entries[3].func()
    assert(WaterTradeForeverDB.classOffers[class]=='both' and dropdown.selected=='Food and water')
end
SlashCmdList.WATERTRADEFOREVER('settings')
assert(#widgets==12)
widgets[12].scripts.OnClick()
assert(next(WaterTradeForeverDB.classOffers)==nil)
assert(widgets[10].selected=='Food and water')
widgets[2].checked=false; widgets[2].scripts.OnClick(widgets[2])
assert(WaterTradeForeverDB.enabled==false)
""")
print('PASS settings opening, per-class dropdown callbacks, reuse, reset and enable toggle')
