-- Ordinary saved macros: creation only, never spell execution or automatic edits.
WaterboyMage = {}
local M = WaterboyMage
local templates = {
    {"Counterspell",2139,"enemy","Interrupt your chosen enemy. Optional stopcasting cancels your current cast."},
    {"Polymorph",118,"enemy","Crowd control your chosen enemy. Damage can break Polymorph."},
    {"Decurse",475,"friend","Remove a curse from a friendly unit, with a self fallback."},
    {"Intellect",1459,"friend","Buff a friendly unit, with a self fallback."},
    {"IceBarrier",11426,"self","Cast Ice Barrier if learned through talents."},
    {"IceBlock",11958,"block","Stop casting and enter Ice Block. Press again to cancel; repeated presses end protection."},
    {"CancelBlock",11958,"cancel","Remove Ice Block when you choose to; this ends its protection."},
    {"Blink",1953,"escape","Stop casting, leave Ice Block and Blink in your facing direction."},
    {"FrostNova",122,"escape","Stop casting, leave Ice Block and freeze nearby enemies."},
    {"Evocation",12051,"channel","Channel Evocation; repeated presses do not restart an active channel."},
    {"ConjureWater",5504,"self","Conjure water at the highest learned rank."},
    {"ConjureFood",587,"self","Conjure food at the highest learned rank."},
    {"Frostbolt",116,"target","Cast your highest learned Frostbolt rank."},
    {"Fireball",133,"target","Cast your highest learned Fireball rank."},
    {"ArcExplosion",1449,"self","Cast Arcane Explosion around you."},
    {"MageArmor",6117,"self","Cast Mage Armor if learned."},
    {"FrostArmor",168,"self","Cast Frost Armor."},
    {"ManaShield",1463,"self","Cast Mana Shield; absorbed damage consumes mana."},
    {"ConjureBoth",5504,"conjure","Conjure water normally; hold Shift or right-click for food."},
    {"Blizzard",10,"cursor","Cast Blizzard at the cursor without a targeting click. Check your cursor position."},
    {"Wand",5019,"wand","Start wand shooting; repeated presses do not toggle shooting off."},
    {"SlowFall",130,"slowfall","Dismount and Slow Fall on yourself; Shift cancels it. Requires a Light Feather."},
    {"TeleSW",3561,"self","Teleport to Stormwind; requires the spell and a Rune of Teleportation."},
    {"TeleIF",3562,"self","Teleport to Ironforge; requires the spell and a Rune of Teleportation."},
    {"TeleDarn",3565,"self","Teleport to Darnassus; requires the spell and a Rune of Teleportation."},
    {"TeleOrg",3567,"self","Teleport to Orgrimmar; requires the spell and a Rune of Teleportation."},
    {"TeleUC",3563,"self","Teleport to Undercity; requires the spell and a Rune of Teleportation."},
    {"TeleTB",3566,"self","Teleport to Thunder Bluff; requires the spell and a Rune of Teleportation."},
    {"PortalSW",10059,"self","Open a Stormwind portal; requires the spell and a Rune of Portals."},
    {"PortalIF",11416,"self","Open an Ironforge portal; requires the spell and a Rune of Portals."},
    {"PortalDarn",11419,"self","Open a Darnassus portal; requires the spell and a Rune of Portals."},
    {"PortalOrg",11417,"self","Open an Orgrimmar portal; requires the spell and a Rune of Portals."},
    {"PortalUC",11418,"self","Open an Undercity portal; requires the spell and a Rune of Portals."},
    {"PortalTB",11420,"self","Open a Thunder Bluff portal; requires the spell and a Rune of Portals."},
}
M.templates = templates
local function Options()
    WaterTradeForeverDB = WaterTradeForeverDB or {}
    if type(WaterTradeForeverDB.mage) ~= "table" then WaterTradeForeverDB.mage = {} end
    local o = WaterTradeForeverDB.mage
    if o.character == nil then o.character = true end
    if o.stopcast == nil then o.stopcast = true end
    if o.mouseover == nil then o.mouseover = true end
    if o.enemy ~= "focus" and o.enemy ~= "mouseover" then o.enemy = "target" end
    return o
end
local function Spell(id)
    if C_Spell and C_Spell.GetSpellName then return C_Spell.GetSpellName(id) end
    if GetSpellInfo then return GetSpellInfo(id) end
end
function M.Build(index)
    local t, o = templates[index], Options()
    if not t then return nil, "Select a macro." end
    local spell = Spell(t[2])
    if not spell then return nil, "Spell data unavailable. Try again after logging in." end
    local body = "#showtooltip " .. spell .. "\n"
    if t[3] == "cancel" then return body .. "/cancelaura " .. spell end
    if t[3] == "conjure" then
        local foodSpell = Spell(587)
        if not foodSpell then return nil, "Food spell data unavailable." end
        return "#showtooltip\n/cast [mod:shift][btn:2] " .. foodSpell .. "; " .. spell
    elseif t[3] == "slowfall" then
        return body .. "/dismount [nomod:shift]\n/cancelaura [mod:shift] " .. spell .. "\n/cast [nomod:shift,@player] " .. spell
    elseif t[3] == "wand" then
        return body .. "/cast !" .. spell
    elseif t[3] == "cursor" then
        return body .. "/cast [@cursor] " .. spell
    elseif t[3] == "channel" then
        return body .. "/cast [nochanneling] " .. spell
    end
    if (t[1] == "Counterspell" and o.stopcast) or t[3] == "block" or t[3] == "escape" then
        body = body .. "/stopcasting\n"
    end
    if t[3] == "block" or t[3] == "escape" then
        local block = Spell(11958)
        if not block then return nil, "Ice Block spell data unavailable." end
        body = body .. "/cancelaura " .. block .. "\n"
    end
    if t[1] == "Polymorph" then body = body .. "/stopattack\n" end
    local condition = ""
    if t[3] == "enemy" and o.enemy ~= "target" then
        condition = "[@" .. o.enemy .. ",harm,nodead][] "
    elseif t[3] == "friend" then
        condition = o.mouseover and "[@mouseover,help,nodead][help,nodead][@player] " or "[help,nodead][@player] "
    end
    return body .. "/cast " .. condition .. spell
end
function M.Create(index)
    if InCombatLockdown() then return false, "Leave combat before creating macros." end
    local _, class = UnitClass("player")
    if class ~= "MAGE" then return false, "Macro creation is available on mage characters." end
    if not (CreateMacro and GetMacroInfo and GetNumMacros and MAX_ACCOUNT_MACROS and MAX_CHARACTER_MACROS) then
        return false, "Macro API unavailable on this client. Copy the preview into /macro."
    end
    local body, err = M.Build(index)
    if not body then return false, err end
    if #body > 255 then return false, "Macro exceeds 255 bytes. Copy and shorten it in /macro." end
    local name = "WB " .. templates[index][1]
    -- Inspect both scopes, including duplicate names. Never overwrite user content.
    for i = 1, MAX_ACCOUNT_MACROS + MAX_CHARACTER_MACROS do
        if GetMacroInfo(i) == name then return false, name .. " already exists. Edit or rename it in /macro first." end
    end
    local account, character = GetNumMacros()
    local perCharacter = Options().character
    if (perCharacter and character >= MAX_CHARACTER_MACROS) or (not perCharacter and account >= MAX_ACCOUNT_MACROS) then
        return false, "Selected macro storage is full. Free a slot in /macro or change storage."
    end
    local ok, id = pcall(CreateMacro, name, 134400, body, perCharacter)
    if not ok or not id or id == 0 then return false, "Client rejected creation. Copy the preview into /macro." end
    local savedName, _, savedBody = GetMacroInfo(id)
    if savedName ~= name or savedBody ~= body then return false, "Could not verify the saved macro. Inspect /macro before using it." end
    return true, "Created " .. name .. ". Open /macro and drag it onto your action bar."
end
local water = {5350,2288,2136,3772,8077,8078,8079}
local food = {5349,1113,1114,1487,8075,8076,22895}
local function Count(ids)
    local total = 0
    local get = C_Item and C_Item.GetItemCount or GetItemCount
    if get then for _, id in ipairs(ids) do total = total + (get(id, false) or 0) end end
    return total
end
local panel, selected = nil, 1
function M.Open()
    local o = Options()
    if not panel then
        panel = CreateFrame("Frame", "WaterboyMageToolkit", UIParent, "BasicFrameTemplateWithInset")
        panel:SetSize(650, 540); panel:SetPoint("CENTER"); panel:SetMovable(true); panel:EnableMouse(true)
        panel:RegisterForDrag("LeftButton"); panel:SetScript("OnDragStart", panel.StartMoving); panel:SetScript("OnDragStop", panel.StopMovingOrSizing)
        panel.TitleText:SetText("Waterboy Forever - Mage Toolkit")
        UISpecialFrames[#UISpecialFrames + 1] = "WaterboyMageToolkit"
        local function Text(x,y,width,text)
            local f = panel:CreateFontString(nil,"OVERLAY","GameFontHighlight")
            f:SetPoint("TOPLEFT",x,y); f:SetWidth(width); f:SetJustifyH("LEFT"); f:SetText(text or ""); return f
        end
        local function Button(x,y,width,label,fn)
            local b = CreateFrame("Button",nil,panel,"UIPanelButtonTemplate")
            b:SetPoint("TOPLEFT",x,y); b:SetSize(width,25); b:SetText(label); b:SetScript("OnClick",fn); return b
        end
        panel.supplies = Text(20,-40,610)
        Button(20,-86,190,"Refreshment trade settings",WaterboyOpenTradeSettings)
        Text(20,-126,610,"Mage macro library — choose a template, review it, then create it.")
        panel.dropdown = CreateFrame("Frame",nil,panel,"UIDropDownMenuTemplate")
        panel.dropdown:SetPoint("TOPLEFT",4,-150); UIDropDownMenu_SetWidth(panel.dropdown,220)
        UIDropDownMenu_Initialize(panel.dropdown,function()
            for i,t in ipairs(templates) do
                local info = UIDropDownMenu_CreateInfo()
                info.text = Spell(t[2]) or t[1]
                if t[3] == "conjure" then info.text = "Conjure water / food" end
                if t[3] == "cancel" then info.text = "Cancel " .. info.text end
                info.checked = selected == i
                info.func = function() selected = i; panel.Refresh() end
                UIDropDownMenu_AddButton(info)
            end
        end)
        panel.enemy = Button(300,-153,320,"",function()
            local opts = Options(); opts.enemy = opts.enemy == "target" and "focus" or opts.enemy == "focus" and "mouseover" or "target"; panel.Refresh()
        end)
        local function Check(y,label,key)
            local c = CreateFrame("CheckButton",nil,panel,"UICheckButtonTemplate")
            c:SetPoint("TOPLEFT",20,y); c.text:SetText(label)
            c:SetScript("OnClick",function(self) Options()[key] = self:GetChecked() and true or false; panel.Refresh() end)
            return c
        end
        panel.character = Check(-190,"Save macros for this character (unchecked: account-wide)","character")
        panel.stopcast = Check(-220,"Counterspell interrupts my current cast","stopcast")
        panel.mouseover = Check(-250,"Mouseover first for Intellect and Remove Lesser Curse","mouseover")
        panel.description = Text(20,-291,610)
        local scroll = CreateFrame("ScrollFrame",nil,panel,"UIPanelScrollFrameTemplate")
        scroll:SetPoint("TOPLEFT",24,-330); scroll:SetSize(580,100)
        panel.preview = CreateFrame("EditBox",nil,scroll)
        panel.preview:SetMultiLine(true); panel.preview:SetFontObject(ChatFontNormal); panel.preview:SetWidth(570); panel.preview:SetAutoFocus(false)
        panel.preview:SetScript("OnEscapePressed",function(self) self:ClearFocus() end)
        -- Preview is copyable; changes are discarded so creation always uses the template.
        panel.preview:SetScript("OnTextChanged",function(self,user) if user then self:SetText(M.Build(selected) or "") end end)
        scroll:SetScrollChild(panel.preview)
        Button(20,-448,150,"Create macro",function() local _,message = M.Create(selected); panel.status:SetText(message) end)
        Button(180,-448,160,"Select text to copy",function() panel.preview:SetFocus(); panel.preview:HighlightText() end)
        panel.length = Text(370,-454,240)
        panel.status = Text(20,-486,610)
        function panel.Refresh()
            local opts,t = Options(),templates[selected]
            UIDropDownMenu_SetText(panel.dropdown,t[1])
            panel.enemy:SetText("Enemy priority: " .. opts.enemy .. " (click to cycle)")
            for _,key in ipairs({"character","stopcast","mouseover"}) do panel[key]:SetChecked(opts[key]) end
            local body,err = M.Build(selected)
            panel.preview:SetText(body or ""); panel.preview:ClearFocus()
            panel.description:SetText(t[4])
            panel.length:SetText(body and (#body .. "/255 bytes") or "")
            panel.status:SetText(err or "Needs the learned spell. Focus/mouseover falls back to target. /macro to place.")
        end
        panel:SetScript("OnShow",panel.Refresh)
        panel:RegisterEvent("BAG_UPDATE_DELAYED")
        panel:SetScript("OnEvent",function() if panel:IsShown() then M.UpdateSupplies() end end)
    end
    panel.Refresh(); M.UpdateSupplies(); panel:Show()
end
function M.UpdateSupplies()
    if panel then panel.supplies:SetText(string.format("In bags: %d water | %d food\nReagents: %d teleport runes | %d portal runes | %d arcane powder",Count(water),Count(food),Count({17031}),Count({17032}),Count({17020}))) end
end
SLASH_WATERBOYMAGE1 = "/mageboy"
SlashCmdList.WATERBOYMAGE = M.Open

-- A discoverable entry in the game's AddOns options; slash commands also work.
local settingsLoader = CreateFrame("Frame")
settingsLoader:RegisterEvent("PLAYER_LOGIN")
settingsLoader:SetScript("OnEvent",function(self)
    self:UnregisterEvent("PLAYER_LOGIN")
    local entry = CreateFrame("Frame")
    entry.name = "Waterboy Forever"
    local title = entry:CreateFontString(nil,"OVERLAY","GameFontNormalLarge")
    title:SetPoint("TOPLEFT",16,-16); title:SetText("Waterboy Forever - Mage Toolkit")
    local open = CreateFrame("Button",nil,entry,"UIPanelButtonTemplate")
    open:SetPoint("TOPLEFT",16,-55); open:SetSize(220,28); open:SetText("Open mage toolkit")
    open:SetScript("OnClick",function()
        if SettingsPanel then SettingsPanel:Hide() end
        if InterfaceOptionsFrame then InterfaceOptionsFrame:Hide() end
        M.Open()
    end)
    if Settings and Settings.RegisterCanvasLayoutCategory and Settings.RegisterAddOnCategory then
        local category = Settings.RegisterCanvasLayoutCategory(entry,entry.name)
        Settings.RegisterAddOnCategory(category)
    elseif InterfaceOptions_AddCategory then InterfaceOptions_AddCategory(entry) end
end)
