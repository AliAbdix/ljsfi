#
#  - uses a module (platform23) maintained by Marc-Andre Lemburg and distributed in Python versions >= 2.3
#
from IntAttr import *
from Base    import *
import StringAttr,Platform
import resource,platform23

class SystemWordSize(StringAttr.StringEQ):
	type  = 'system word size in bits'
	title = 'System Word Size in Bits'
	action = 'test system word size in bits'
	
	def val(self): 
		return platform23.architecture()[0][:2]
	
class CPU(StringAttr.StringEQ):
	type  = 'system processor'
	title = 'System Processor'
	action = 'test system processor'
	
	def val(self): 
                # Swapped from platform23.machine to allow for pretend-arch (Scot Kronenfeld 2/2009)
		return Platform.thisArch()
	
class ByteOrder(StringAttr.StringEQ):
	type = 'system byte order'
	title = 'System Byte Order'
	action = 'test system byte order'
	
	def val(self): return sys.byteorder
	
class SystemVersionEQ(StringAttr.StringEQ):
	type = 'system version'
	title = 'System Version'
	action = 'test system version'
	
	def val(self): return platform23.version()
	
class SystemVersionLE(StringAttr.StringLE):
	type = 'system version <='
	title = 'System Version <='
	action = 'test system version <='
	
	def val(self): return platform23.version()
	
class SystemVersionLT(StringAttr.StringLT):
	type = 'system version <'
	title = 'System Version <'
	action = 'test system version <'
	
	def val(self): return platform23.version()
	
class SystemVersionGE(StringAttr.StringGE):
	type = 'system version >='
	title = 'System Version >='
	action = 'test system version >='
	
	def val(self): return platform23.version()
	
class SystemVersionGT(StringAttr.StringGT):
	type = 'system version >'
	title = 'System Version >'
	action = 'test system version >'
	
	def val(self): return platform23.version()
	
class SystemReleaseEQ(StringAttr.StringEQ):
	type = 'system release string'
	title = 'System Release String'
	action = 'test system release string'
	
	def val(self): return platform23.release()
	
class SystemReleaseLE(StringAttr.StringLE):
	type = 'system release string <='
	title = 'System Release String <='
	action = 'test system release string'
	
	def val(self): return platform23.release()
	
class SystemReleaseLT(StringAttr.StringLT):
	type = 'system release string <'
	title = 'System Release String <'
	action = 'test system release string <'
	
	def val(self): return platform23.release()
	
class SystemReleaseGE(StringAttr.StringGE):
	type = 'system release string >='
	title = 'System Release String >='
	action = 'test system release string >='
	
	def val(self): return platform23.release()
	
class SystemReleaseGT(StringAttr.StringGT):
	type = 'system release string >'
	title = 'System Release String >'
	action = 'test system release string >'
	
	def val(self): return platform23.release()
	
class PythonCompiler(StringAttr.StringEQ):
	type = 'compiler used to compile Python'
	title = 'Compiler Used to Compile Python'
	action = 'test compiler used to compile Python'
	
	def val(self): return platform23.python_compiler()

class CPUSecondsMaximumSoftGE(IntAttr):
	type   = 'CPU seconds soft maximum >='
	title  = 'CPU Seconds Soft Maximum >='
	action = 'CPU seconds soft maximum >='
	
	def satisfied(self):
		limit = resource.getrlimit(resource.RLIMIT_CPU)[0]
		if limit>0 and limit<self.value: return Reason('CPU maximum ['+`limit`+'] seconds soft limit is less than ['+`self`+'].')
		else:                            return Reason()
#	def satisfiable(self): return self.satisfied()
	
class CPUSecondsMaximumHardGE(IntAttr):
	type   = 'CPU seconds hard maximum >='
	title  = 'CPU Seconds Hart Maximum >='
	action = 'CPU seconds hard maximum >='
	
	def satisfied(self):
		limit = resource.getrlimit(resource.RLIMIT_CPU)[1]
		if limit>0 and limit<self.value: return Reason('CPU maximum ['+`limit`+'] seconds hard limit is less than ['+`self`+'].')
		else:                            return Reason()
#	def satisfiable(self): return self.satisfied()
	
class CPUSecondsMaximumGE(CPUSecondsMaximumSoftGE):
	type   = 'CPU seconds maximum >='
	title  = 'CPU Seconds Maximum >='
	action = 'CPU seconds soft maximum >='

class FileSizeMaximumSoftGE(IntAttr):
	type   = 'file size soft maximum in bytes >='
	title  = 'File Size Soft Maximum in Bytes >='
	action = 'file size soft maximum in bytes >='
	
	def satisfied(self):
		limit = resource.getrlimit(resource.RLIMIT_FSIZE)[0]
		if limit>0 and limit<self.value: return Reason('File size soft maximum ['+`limit`+'] bytes is less than ['+`self`+'].')
		else:                            return Reason()
#	def satisfiable(self): return self.satisfied()
	def acquire(self): return self.satisfied()
	def retract(self): return Reason()

class FileSizeMaximumHardGE(IntAttr):
	type   = 'file size hard maximum in bytes >='
	title  = 'File Size Hard Maximum in Bytes >='
	action = 'file size hard maximum in bytes >='
	
	def satisfied(self):
		limit = resource.getrlimit(resource.RLIMIT_FSIZE)[1]
		if limit>0 and limit<self.value: return Reason('File size hard maximum ['+`limit`+'] bytes is less than ['+`self`+'].')
		else:                            return Reason()
#	def satisfiable(self): return self.satisfied()
	def acquire(self): return self.satisfied()
	def retract(self): return Reason()

class FileSizeMaximumGE(FileSizeMaximumSoftGE):
	type   = 'file size maximum in bytes >='
	title  = 'File Size Maximum in Bytes >='
	action = 'file size maximum in bytes >='

class HeapSizeMaximumGE(IntAttr):
	type   = 'heap size maximum in bytes >='
	title  = 'Heap Size Maximum in Bytes >='
	action = 'heap size maximum in bytes >='
	
	def satisfied(self):
		limit = resource.getrlimit(resource.RLIMIT_DATA)[0]
		if limit>0 and limit<self.value: return Reason('Heap size maximum ['+`limit`+'] bytes is less than ['+`self`+'].')
		else:                            return Reason()
#	def satisfiable(self): return self.satisfied()
	def acquire(self): return self.satisfied()
	def retract(self): return Reason()

class StackSizeMaximumGE(IntAttr):
	type   = 'stack size maximum in bytes >='
	title  = 'Stack Size Maximum in Bytes >='
	action = 'stack size maximum in bytes >='
	
	def satisfied(self):
		limit = resource.getrlimit(resource.RLIMIT_STACK)[0]
		if limit>0 and limit<self.value: return Reason('Stack size maximum ['+`limit`+'] bytes is less than ['+`self`+'].')
		else:                            return Reason()
#	def satisfiable(self): return self.satisfied()
			
class ImageSizeMaximumGE(IntAttr):
	type   = 'image size maximum in bytes >='
	title  = 'Image Size Maximum in Bytes >='
	action = 'image size maximum in bytes >='
	
	def satisfied(self):
		h_limit = resource.getrlimit(resource.RLIMIT_DATA) [0]
		s_limit = resource.getrlimit(resource.RLIMIT_STACK)[0]

		if   (h_limit>0 and h_limit<self.value):
			return Reason('Heap size limit ['+`h_limit`+'] is less than ['+`self`+'].')
		elif (s_limit>0 and s_limit<self.value): 
			return Reason('Stack size limit ['+`s_limit`+'] is less than ['+`self`+'].')
		else:				       
			return Reason()
#	def satisfiable(self): return self.satisfied()
	def acquire(self): return self.satisfied()
	def retract(self): return Reason()
	
class OpenFileDescriptorsMaximumSoftGE(IntAttr):
	type   = 'soft maximum number of open file descriptors >='
	title  = 'Soft Maximum Number of Open File Descriptors >='
	action = 'soft maximum number of open file descriptors >='
	
	def satisfied(self):
		limit = resource.getrlimit(resource.RLIMIT_NOFILE)[0]
		
		if   (limit>0 and limit<self.value): return Reason('Soft maximum number of open file descriptors ['+`limit`+'] is less than ['+`self`+'].')
		else:                                return Reason()
#	def satisfiable(self): return self.satisfied()
	def acquire(self): return self.satisfied()
	def retract(self): return Reason()
	
	
class OpenFileDescriptorsMaximumHardGE(IntAttr):
	type   = 'hard maximum number of open file descriptors >='
	title  = 'Hard Maximum Number of Open File Descriptors >='
	action = 'Hard maximum number of open file descriptors >='
	
	def satisfied(self):
		limit = resource.getrlimit(resource.RLIMIT_NOFILE)[0]
		
		if   (limit>0 and limit<self.value): return Reason('Hard maximum number of open file descriptors ['+`limit`+'] is less than ['+`self`+'].')
		else:                                return Reason()
	def acquire(self): return self.satisfied()
	def retract(self): return Reason()
	
class OpenFileDescriptorsMaximumGE(OpenFileDescriptorsMaximumSoftGE):
	type   = 'maximum number of open file descriptors >='
	title  = 'Maximum Number of Open File Descriptors >='
	action = 'maximum number of open file descriptors >='
	
