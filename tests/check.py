from pathlib import Path
from lupa import LuaRuntime

source = (Path(__file__).resolve().parents[1] / 'WaterboyForever.lua').read_text()
def setup():
    lua = LuaRuntime()
    lua.execute('''
    SlashCmdList = {}; NUM_BAG_SLOTS = 0; timers = {}; offered = 0; trades = {}
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
    function ClearCursor() cursor=nil end
    function GetTradePlayerItemInfo(slot) if slot==1 then return trade end end
    function ClickTradeButton(slot) offered=offered+1; trades[slot]=cursor; trade=cursor; cursor=nil end
    TradeFrame = {IsShown=function() return visible end}
    C_Timer = {After=function(_, f) timers[#timers+1]=f end}
    C_Container = {
      GetContainerNumSlots=function() return #bags end,
      GetContainerItemInfo=function(_, slot) return bags[slot] end,
      PickupContainerItem=function(_, slot) cursor=bags[slot].itemID end
    }
    C_Item = {GetItemInfo=function(id)
      return 'water','link',1,1,(id==3772 and 25 or 1),nil,nil,20
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
    ('rogue', "class='ROGUE'; bags[3]={itemID=1113, stackCount=20}", 'offered==0'),
    ('shapeshifted druid', "class='DRUID'", 'offered==1'),
    ('partial stacks', 'bags[1].stackCount=19; bags[2].stackCount=5', 'offered==0'),
    ('populated trade', 'trade=123', 'offered==0 and trade==123'),
    ('busy cursor', 'cursor=123', 'offered==0 and cursor==123'),
    ('combat', 'combat=true', 'offered==0'),
    ('disabled', 'WaterTradeForeverDB.enabled=false', 'offered==0'),
    ('locked bags', 'bags[2].isLocked=true', 'offered==0'),
]
for label, before, assertion in cases:
    lua = setup()
    lua.execute(before + "; event('TRADE_SHOW'); flush(); assert(" + assertion + ")")
    print('PASS', label)
lua = setup()
lua.execute("event('TRADE_SHOW'); event('TRADE_CLOSED'); flush(); assert(offered==0)")
lua.execute("event('TRADE_SHOW'); timers[1](); trade=nil; flush(); assert(offered==1)")
lua.execute("event('TRADE_CLOSED'); event('TRADE_SHOW'); flush(); assert(offered==2)")
print('PASS cancellation, removal and next trade')
lua = setup()
lua.execute("event('TRADE_SHOW'); event('TRADE_ACCEPT_UPDATE',1,0); flush(); assert(offered==0)")
print('PASS accepted trade remains untouched')
