from cum.scrapers.batoto import BatotoChapter, BatotoSeries
from cum.scrapers.dynastyscans import DynastyScansChapter, DynastyScansSeries
from cum.scrapers.madokami import MadokamiChapter, MadokamiSeries
from cum.scrapers.fumanhua import FuManHuaSeries, FuManHuaChapter
from cum.scrapers.c99comic import C99ComicSeries, C99ComicChapter
from cum.scrapers.c99manga import C99MangaSeries, C99MangaChapter

series_scrapers = [BatotoSeries, DynastyScansSeries, MadokamiSeries,
                   FuManHuaSeries, C99ComicSeries, C99MangaSeries]
chapter_scrapers = [BatotoChapter, DynastyScansChapter, MadokamiChapter,
                    FuManHuaChapter, C99ComicChapter, C99MangaChapter]
