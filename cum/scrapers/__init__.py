from cum.scrapers.batoto import BatotoChapter, BatotoSeries
from cum.scrapers.dynastyscans import DynastyScansChapter, DynastyScansSeries
from cum.scrapers.madokami import MadokamiChapter, MadokamiSeries
from cum.scrapers.fumanhua import FuManHuaSeries, FuManHuaChapter
from cum.scrapers.c99comic import C99ComicSeries, C99ComicChapter

series_scrapers = [BatotoSeries, DynastyScansSeries, MadokamiSeries,
                   FuManHuaSeries, C99ComicSeries]
chapter_scrapers = [BatotoChapter, DynastyScansChapter, MadokamiChapter,
                    FuManHuaChapter, C99ComicChapter]
