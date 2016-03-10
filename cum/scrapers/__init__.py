from cum.scrapers.batoto import BatotoChapter, BatotoSeries
from cum.scrapers.dynastyscans import DynastyScansChapter, DynastyScansSeries
from cum.scrapers.madokami import MadokamiChapter, MadokamiSeries
from cum.scrapers.fumanhua import FuManHuaSeries, FuManHuaChapter

series_scrapers = [BatotoSeries, DynastyScansSeries, MadokamiSeries,
                   FuManHuaSeries]
chapter_scrapers = [BatotoChapter, DynastyScansChapter, MadokamiChapter,
                    FuManHuaChapter]
