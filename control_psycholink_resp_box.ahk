#SingleInstance

; ahk script for controlling psycholink from inside the meg scanner

1::send {LEFT}
2::send {C}
3::send {A}

4::
 {
   count++
   settimer, actions, 500
 }
return

actions:
 {
   if (count = 1)
    {
      send {SPACE}
    }
   else if (count = 2)
    {
      send {ENTER}
    }
   else if (count = 3)
    {
      send {ESCAPE}
    }
   count := 0
 }
return