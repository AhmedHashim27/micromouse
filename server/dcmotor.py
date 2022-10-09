class DCMotor:      
	def __init__(self, pin1, pin2, enable_pin, min_duty=240, max_duty=1023):
		self.pin1=pin1
		self.pin2=pin2
		self.enable_pin=enable_pin
		self.min_duty = min_duty
		self.max_duty = max_duty

	def forward(self,speed):
		self.speed = speed
		self.enable_pin.duty(self.duty_cycle(self.speed))
		self.pin1.value(0)
		self.pin2.value(1)
	
	def backwards(self, speed):
		self.speed = speed
		self.enable_pin.duty(self.duty_cycle(self.speed))
		self.pin1.value(1)
		self.pin2.value(0)

	def stop(self):
		self.enable_pin.duty(0)
		self.pin1.value(0)
		self.pin2.value(0)
		
	def duty_cycle(self, s):
		if s <= 0 or s > 100:
			duty_cycle = 0
		else:
			duty_cycle = int(self.min_duty + (self.max_duty - self.min_duty)*((s-1)/(100-1)))
			return duty_cycle
