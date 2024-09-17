
import os
from swatmf.handler import read_from, file_name, copy_file, write_to

class Cl(object):
    
    def __init__(self, wd):
        """weather dataset

        Args:
            wd (path): weather dataset path
        """
        os.chdir(wd)

    def create_swat_climates(self, infcsv, clin, clout):
        fc = read_from(infcsv)
        print(fc)
        for line in fc[1:]:
            fileName = f'{line.split(",")[1]}.txt'
            print(fileName)
            print(len(read_from(os.path.join(clin, f"./pcp/{fileName}"))))
            copy_file(os.path.join(clin, f"./pcp/{fileName}"), f"{clout}/{file_name(fileName)}")
        write_to(f"{clout}/pcp.txt", "".join(fc))
        newFC = f"{fc[0].strip()}\n"
        for line in fc[1:]:
            fileName = f'{line.split(",")[1]}.txt'
            newName = f'{line.split(",")[1]}_TMP.txt'
            newFC += f'{line.split(",")[0]},{file_name(newName, extension=False)},{line.split(",")[2]},{line.split(",")[3]},{line.split(",")[4].strip()}\n'
            copy_file(os.path.join(clin, f"./tmp/{fileName}"), f"{clout}/{file_name(newName)}")
        write_to(f"{clout}/tmp.txt", newFC)


if __name__ == '__main__':
    wd = "D:\\Projects\\Africa_data\\AF_CHIRPS_weather"
    infile = "Africa_grids.csv"
    # # dawena
    # lats = [5.6, 5.9]
    # lons = [0.01, 0.1]

    # botanga
    lats = [9.25,  9.37]
    lons = [-1.25, -1.17]
    outf = 'cdbotanga.csv'
    m01 = Cl(wd)
    df_co = m01.check_coordinates(infile, lats, lons, outf)
    print(df_co)
    infcsv = "D:\\Projects\\Africa_data\\AF_CHIRPS_weather\\cdbotanga.csv"
    clin = "D:\\Projects\\Africa_data\\AF_CHIRPS_weather\\AF"
    clout = "D:\\Projects\\Africa_data\\botanaga_weather"
    m01.create_swat_climates(infcsv, clin, clout)