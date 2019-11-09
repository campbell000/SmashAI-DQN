---
--- Created by ascam.
--- DateTime: 12/11/2017 9:27 PM
---
List = {}
function List.newList ()
    return {first = 0, last = -1}
end

function List.length(T)
    local count = 0
    for _ in pairs(T) do count = count + 1 end
    return count - 2 -- Minus 2 for the "first" and "last" elements
end

function List.pushleft (list, value)
    local first = list.first - 1
    list.first = first
    list[first] = value
end

function List.pushright (list, value)
    local last = list.last + 1
    list.last = last
    list[last] = value
end

function List.empty(list)
    while (List.length(list) > 0) do
        List.popleft(list)
    end
end

function List.popleft (list)
    local first = list.first
    if first > list.last then error("list is empty") end
    local value = list[first]
    list[first] = nil        -- to allow garbage collection
    list.first = first + 1
    return value
end

function List.popright (list)
    local last = list.last
    if list.first > last then error("list is empty") end
    local value = list[last]
    list[last] = nil         -- to allow garbage collection
    list.last = last - 1
    return value
end

function List.copy(source)
    local newCopy = List.newList()
    for state_num = 1, List.length(source) do
        local element = List.popleft(source)
        List.pushright(source, element)
        List.pushright(newCopy, element)
    end
    return newCopy
end

function List.dump(source)
    for state_num = 1, List.length(source) do
        local a = List.popleft(source)
        print(a)
        List.pushright(source,a)
    end
end


