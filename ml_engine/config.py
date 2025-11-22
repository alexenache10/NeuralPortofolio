# hyperparameters

# Data configurations
SEQUENCE_LENGTH = 60    # we only look back to the past 60 days
TEST_SIZE = 0.2         
FEATURE_COLUMNS = ['open', 'high', 'low', 'close', 'volume']
TARGET_COLUMN = 'close' # we need to predict the close price

# Model configurations
HIDDEN_SIZE = 64        
NUM_LAYERS = 2          
DROPOUT = 0.2
BATCH_SIZE = 32
LEARNING_RATE = 0.001
EPOCHS = 20