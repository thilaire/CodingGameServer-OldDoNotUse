"""
This file is a template for a new training player in your game

it should be imported by your game, and add in the `type_dict` dictionary
"""

from server.Player import TrainingPlayer


class TemplateTrainingPlayer(TrainingPlayer):
	"""
	class TemplateTrainingPlayer

	Inherits from TrainingPlayer
	"""

	def __init__(self, **options):
		"""
		Initialize the Training Player

		You may use the options dictionary
		"""
		super().__init__('Do_nothing')
		#
		# insert your code here to get/validate/store the options...
		#


	def playMove(self):
		"""
		Returns the move to play (string)
		"""
		#
		# insert your code here to find which move you want to do...
		#
		return ""

