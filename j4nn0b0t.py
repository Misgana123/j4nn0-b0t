 #!/usr/bin/env python
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import sqlite3

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

GENDER, PHOTO, LOCATION, BIO = range(4)

questions = ['መመሪያዎች፡\n'
'1) ጥያቄዎቹን መመለስ የሚቻለው በአማርኛ ቋንቋ ብቻ ነው፡፡\n'
'2) ጥያቄዎቹን ሰፋ ባለ መልኩ ይመልሱልን (ከ2 እስከ 3 አረፍተ ነገሮችን ወይም 1 ሰፋ ያለ አረፍተነገር)\n\n'
'ምሳሌ፡\n'
'ጥያቄ ፡ ስልክዎ ሳያውቁት የሞሉትን የሞባይል ካርድ ይበላቦታል (ይወስድቦታል)፡፡ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡ ስልኬ የሞላሁትን ካርድ ሳልጠቀምበት እየበላብኝ ነው፡፡ ምንድነው ችግሩ?\n\n'
'ወደጥያቄዎቹ ለመቀጠል ይህንን => /continue ይጫኑ'
,'ጥያቄ ፡ ስልክዎ ላይ ካርድ ለመሙላት ቢያስቸግርዎ (ስልክዎ ካርድ አልሞላ ቢልዎት)፡፡ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡'
, 'ጥያቄ ፡ስልክዎ የሞሉትን የሞባይል ካርድ ቢበላብዎት(የሞባይልዎ የአየር ሰአት/ብር/ ቢቀንስ)፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡'
, 'ጥያቄ ፡ የጥሪ ማሳመሪያ አገልግሎት መጠቀም ቢፈልጉ (ማለትም ሰዎች የእስዎ ስልክ ላይ ሲደውሉ ጥሪው ዘፈን፣ መዝሙር ወይም ሙዚቃ እዲሆን ቢፈልጉ)፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡'
, 'ጥያቄ ፡ የጥሪ ማሳመሪያ አገልግሎት ለማቋረጥ ቢፈልጉ (ማለትም ሰዎች የእስዎ ስልክ ላይ ሲደውሉ ጥሪው ዘፈን፣ መዝሙር ወይም ሙዚቃ እዲሆን ቢፈልጉ)፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡'
,
'ጥያቄ ፡ ከቴሌ ላይ የአየር ሰአት (ብር) መበደር ቢፈልጉና ምን ማድረግ እንዳለብዎች መረጃ ለመጠየቅ ቢፈልጉ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ ከቴሌ ላይ የአየር ሰአት (ብር) ለመበደር ሲሞከሩ አልሰራ ቢልዎት፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ ሲም ካርድዎ አልሰራ ቢልዎት፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ የፒዩኬ ኮድ ቁጥርዎን ለመጠየቅ ቢፈልጉ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ የፒን ኮድ ቁጥርዎን ለመጠየቅ ቢፈልጉ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ የሲም ካርድዎ ቢጠፋብዎት ወይም ቢሰረቅብዎት እና ሲም ካርድዎን ለማዘጋት ቢፈልጉ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ እርሶ አዘግተውት የነበረውን ሲም ካርድ በድጋሚ ለማስከፈት ቢፈልጉ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ በራስዎ ስልክ ቁጥር አዲስ ሲም ካርድ ለመግዛት ቢፈልጉ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ የሲም ካርድዎን ባለቤትነት ወደ ሌላ ሰው ለማስቀየር ቢፈልጉ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ የራስዎን ስልክ ቁጥር ስንት እንደሆን ማወቅ ቢፈልጉ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ ለመደወል ሲፈልጉ ስልክዎ አልደውል ቢልዎት፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ ሰዎች ስልክዎ ላይ ሲደውሉ አልሰራ ቢላቸው ወይም እርስዎ ጋር ባይጠራ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ ስልክዎ ላይ ሲም ካርድ ሲያስገቡ አልሰራም ቢልዎት፤ ስልክዎ ‘Insert SIM’ ወይም Emergency Call only ቢልዎት፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ የስልክዎ የሞባይል ኔትዎርክ(ሲግናል) በጣም አነስተኛ(ደካማ) ቢሆን፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ ስልክዎ ሜሴጅ(SMS) አልክ ቢልዎት፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ ሰው ስልክዎ ላይ ሜሴጅ(SMS) ሲልክ ስልክዎ ሜሴጅ(SMS) አልቀበል ቢልዎት፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ ለሰው የሞባይል ብር(የአየር ሰአት) ቢልኩና የተላከለት ስልክ ብሩ(የአየር ሰአቱ) ባይደርሰው፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ ለሰው የሞባይል ብር(የአየር ሰአት) ለመላክ ሲሞክሩ አልሰራ ቢልዎት ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ ሞባይሎ(ስልክዎ) ያለውን የአየር ሰአት (ብር) ለማወቅ ቢፈልጉ ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ ስልክዎ ላይ በተደጋጋሚ የማይፈልጉት ሜሴጅ(SMS) አየገባ ቢያስቸግርዎት፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ የሜሴጅ(SMS) ታሪፍ(ዋጋ) ማወቅ ቢፈልጉ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ የስልክ ጥሪ ታሪፍ(ዋጋ) ማወቅ ቢፈልጉ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ የኢንተርኔት ታሪፍ(ዋጋ) ማወቅ ቢፈልጉ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ የኢንተርኔት አገልግሎት በስልክዎ መጠቀም ቢያቅቶት፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ የማህበራዊ ድህረገጾችን (Social Media) ለመጠቀም ፈልገው ቢያቅቶት፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ ስለ ሞባይል ፓኬጅ መረጃ ማወቅ ቢፈልጉ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ ስልክዎ የሞባይል ፓኬጅ አልሞላ ቢልዎት፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ በስልክዎ የሞሉት የሞባይል ፓኬጅ ቀኑ ሳይደርስ ቢቋረጥ (expire ቢያደርግ)፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ በስልክዎ የሞሉት የሞባይል ፓኬጅ “75% ተጠቅመዋል” የሚል ሜሴጅ ሳይደርስዎት ቢያልቅ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ በስልክዎ የሞሉት የሞባይል ፓኬጅ ወደሌላ ሰው ለማዘዋወር(ለማስተላለፍ) ቢፈልጉ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ በስህተት በስልክዎ የሞሉትን የሞባይል ፓኬጅ ወደሌላ ለመቀየር ወይም ለማስመለስ ቢፈልጉ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ በስልክዎ ላይ የቀረው የሞባይል ፓኬጅ ምን ያህል እንደሆነ ማወቅ ቢፈልጉ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ ስለ ቮይስ ሜይል( Voice Mail) አገልግሎት መረጃ ማወቅ ቢፈልጉ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ በስልክዎ ላይ የቮይስ ሜይል( Voice Mail) አገልግሎት ማስጀመር ቢፈልጉ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ የቮይስ ሜይል(Voice Mail) አገልግሎት ማቋረጥ ቢፈልጉ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ የቮይስ ሜይል(Voice Mail) አገልግሎት አልሰራ ቢልዎት፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ ስልክዎ ላይ ካርድ ሲሞሉ የሲም ካርድዎ የአገልግሎት ቀን(Expiry date) ባይራዘም፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ ስልክዎን ሲጠቀሙ ከተገቢው በላይ ታሪፍ(ብር) ቢያስከፍልዎት፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ ለሰው የሞባይል ፓኬጅ ጊፍት ለመላክ ምን ማድረግ እንዳለቦት መረጃ ማግኘት ቢፈልጉ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ ለሰው የሞባይል ፓኬጅ ጊፍት ለመላክ ፈልገው ስልክዎ አልክ ቢልዎት፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ ለሰው የሞባይል ፓኬጅ ጊፍት ልከው፣ ከእርስዎ ስልክ ላይ ብር ቆርጦ ለተላከለት ሰው ፓኬጁ ባይደርስ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ የCall Conference(በአንድ ጊዜ ብዙ ሰዎችን የማውራት) አገልግሎት መጠቀም ፈልገው ምን ማድረግ እንዳለቦት ለማወቅ ቢፈለጉ ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ የCall Conference(በአንድ ጊዜ ብዙ ሰዎችን የማውራት) አገልግሎት አልሰራ ቢልዎት ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ የCall Conference(በአንድ ጊዜ ብዙ ሰዎችን የማውራት) አገልግሎት ታሪፍ(ዋጋ) ማወቅ ቢፈልጉ ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ የCall Conference(በአንድ ጊዜ ብዙ ሰዎችን የማውራት) አገልግሎት ከሚገባው በላይ ቢያስከፍልዎት ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ Call Me Back (መልሰው ይደውሉልኝ፣ኮል ሚ ባክ) አገልግሎት ለመጠቀም ምን ማድረግ እንዳለቦት ማወቅ ቢፈልጉ ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ ስልክዎ Call Me Back (መልሰው ይደውሉልኝ፣ኮል ሚ ባክ) አልልክ ቢልዎ ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ ስለፍሌክሲ ፓኬጅ(Flexi Packages) መረጃ ማወቅ ቢፈልጉ ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ በስልክዎ ፍሌክሲ ፓኬጅ(Flexi Packages) ለመሙላት ፈልገው መሙላት ቢያስቸግርዎ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ ፍሌክሲ ፓኬጅ(Flexi Packages) ከታሪፍ በላይ ብር ቢበላብዎት፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ ስለ-ይሙሉ የኤሌክትሮኒክ ካርድ መሙያ አገልግሎት መረጃ ማወቅ ቢፈልጉ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ በ-ይሙሉ የኤሌክትሮኒክ ካርድ መሙያ አገልግሎት ካርድ ለመሙላት ቢፈልጉና አልሞላ ቢልዎት፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ የ-ይሙሉ የኤሌክትሮኒክ ካርድ መሙያ አገልግሎት ሻጭ(ቸርቻሪ) ለመሆን ቢፈልጉና ምን ማድረግ እንዳለቦት ለማወቅ ቢፈልጉ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ በስልክዎ የ909 አገልግሎት ለመጠቀም ቢያስቸግርዎ ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ የ994  አገልግሎት በሌላ ቋንቋ መጠቀም ቢፈልጉ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ የ994 የደንበኞችን አገልግሎት ለመጠቀም ቢያስቸግረዎ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ ስለ994 የደንበኞችን አገልግሎት ሰራተኞች አስተያየት ለመስጠት ቢፈልጉ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ የመስመር ስልክ ተጠቅመው መደወል ቢያስቸግርዎ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ የመስመር ስልክዎ ላይ ሲደወል ስልኩ ጥሪ የማይቀበል ከሆነ፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡',
'ጥያቄ ፡ ስልክዎ ወደውጪ ሃገር ለመደወል ካስቸገርዎት፤ በዚህ ጊዜ 994 በመደወል ምን በማለት ይጠይቃሉ?\n\n'
'994፡ ኢትዮ ቴሌኮም ነኝ፡፡ እባክዎን ምን ልርዳዎት?\n\n'
'እርስዎ፡'


]
questionCounter = 0
def loadDB():
    # Creates SQLite database to store info.
    conn = sqlite3.connect('content.sqlite')
    cur = conn.cursor()
    conn.text_factory = str
    cur.executescript('''CREATE TABLE IF NOT EXISTS userdata
    (
    id TEXT, 
    firstname TEXT, 
    lastname TEXT,
    message TEXT,
    username TEXT);'''
    )
    conn.commit()
    conn.close()

def addUser(update):
    # Checks if user has visited the bot before
    # If yes, load data of user
    # If no, then create a new entry in database
    conn = sqlite3.connect('content.sqlite')
    cur = conn.cursor()
    conn.text_factory = str
    
    cur.execute('''INSERT INTO userdata (id, firstname,lastname,message,username) VALUES (?, ?, ?, ?, ?)''', \
    (str(update.message.from_user.id), str(update.message.from_user.first_name), str(update.message.from_user.last_name), 
    str(update.message.text), str(update.message.from_user.username)))
    
    conn.commit()
    conn.close()

def start(update: Update, context: CallbackContext) -> int:
    
    update.message.reply_text(
        'ሰላም! ጃርሶ-ኤአይ (Jarso-AI) እንባላለን፡፡ የኢትዮ ቴሌኮም 994 የደንበኞችን አገልግሎት የተቀላጠፈ ለማድረግ በስራ ላይ እገኛለን፡፡ '
        'እርስዎም በዚህ ስራ ላይ የበኩልዎን በማበርከት እንዲተባበሩን እንጠይቃለን፡፡ \nከዚህ በመቀጠል የሚመጡትን አነስተኛ ጥያቄዎች በጥንቃቄ በማንበብ'
        ' መልስዎን ይላኩልን፡፡ \n\nይህንን ቅጽ በጥንቃቄና በተገቢው ሁኔታ ለሚሞሉ ተባባሪዎቻችን በየቀኑ ከ25 እስከ 200 ብር የሚደርሱ የሞባይል ካርዶችን'
        ' ለባለእድለኞች እንደማበረታቻ ሽልማት የምናቀርብ ይሆናል፡፡\n\n'
        
        'ለመቀጠል ይህንን => /continue ይጫኑ',
        
    )

    return GENDER


def gender(update: Update, context: CallbackContext) -> int:
    global questionCounter
    if questionCounter <=1 and update.message.text != "/continue":
        update.message.reply_text("እባክዎን ከላይ ያሉትን ሊንኮች ብቻ ይጫኑ፡፡")
        return GENDER
    if questionCounter > 1 and (update.message.text.lower().islower() or update.message.text.upper().isupper()):
        update.message.reply_text("ጥያቄዎቹን መሙላት የሚቻለው በአማርኛ ቋንቋ ብቻ ነው፡፡ እባክዎን መልስዎን በአማርኛ ብቻ ይሙሉ፡፡")
        return GENDER
    if len(update.message.text) < 5:
        update.message.reply_text("የሰጡን መልስ በጣም አጭር ነው፡፡ እባክዎን መልስዎን ረዘም ባለ አረፍተነገር/ሮች ይመልሱልን፡፡")
        return GENDER
    user = update.message.from_user
    
    logger.info("Gender of %s: %s", user.first_name, update.message.text)
    try:
        update.message.reply_text(
            questions[questionCounter],
            reply_markup=ReplyKeyboardRemove(),
        )
        if questionCounter > 1:
            
            addUser(update)

        questionCounter += 1
        if questionCounter == 5:
            return BIO
    except Exception as e:
        print("Unexpected error:",str(e),e.__traceback__.tb_lineno)
    return GENDER

def bio(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)

    global questionCounter

    addUser(update)
    questionCounter = 0
    update.message.reply_text('ተጨማሪ ጥያቄዎችን በመሙላት ሊተባበሩን ፈቃደኛ ከሆኑ ይህንን  => /continue ይጫኑ፡፡ \n ለማቋረጥ ከፈለጉ ይህንን => /cancel ይጫኑ፡፡')

    return GENDER


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'ስለትብብርዎ ከልብ እናመሰግናለን፡፡ የሽልማት ባለእድለኞችን እናሳውቆታለን፡፡', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("1578959416:AAHrp6qjT4Qf3PFkkPiNtJ_ORCr0bCWUiRY", use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            GENDER: [MessageHandler(Filters.text & ~Filters.command, gender),CommandHandler('continue', gender)],
            BIO: [MessageHandler(Filters.text & ~Filters.command, bio),CommandHandler('continue', gender)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    loadDB()
    main()
