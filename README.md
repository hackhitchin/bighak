# bighak v2.0
bighak has undergone surgery to replace the wheel chair motor controller 
with more flexible standard high ampage motor controllers.  

## Summary
This project is to re-write the source code to no longer require the 
hard wired controller and use something like a PS3 controller instead.

## Details
We will now use a Raspberry Pi to control everything (like last time) and an 
Arduino connected via USB serial to the Pi to directly talk to the motor controller.  
  
The modular design means the Pi will be sending left/right motor speeds and directions 
to the Arduino in the range of [-1,1]. The Arduino will then interpret that range into 
valid voltage ranges for the motor controllers.  
  
The design means we can swap the controller for other types of controllers like 
Nintendo Wii joysticks with relative ease. All you need do is interpret the new 
controllers min and max joystick values back to a range of [-1,1].
