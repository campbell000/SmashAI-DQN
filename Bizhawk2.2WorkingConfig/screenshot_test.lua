require'clipboard'
for k,v in ipairs(clipboard.getformats() or {}) do
    print(k, v, clipboard.formatname(v))
end



if clipboard.isformatavailable(1) then
    print("FORMAT IS 1")
    print(clipboard.gettext())
end

if clipboard.isformatavailable(2) then
    print("FORMAT IS 2")
    print(clipboard.getdata(2))
end

if clipboard.isformatavailable(3) then
    print("FORMAT IS 3")
    print(clipboard.gettext())
end

if clipboard.isformatavailable(4) then
    print("FORMAT IS 4")
    print(clipboard.gettext())
end

if clipboard.isformatavailable(5) then
    print("FORMAT IS 5")
    print(clipboard.gettext())
end

if clipboard.isformatavailable(6) then
    print("FORMAT IS 6")
    print(clipboard.gettext())
end

if clipboard.isformatavailable(7) then
    print("FORMAT IS 7")
    print(clipboard.gettext())
end


while true do
    client.screenshottoclipboard()
    for k,v in ipairs(clipboard.getformats() or {}) do
        print(k, v, clipboard.formatname(v))
    end

    emu.frameadvance();

    a = clipboard.gettext()
    print(tostring(a))

end