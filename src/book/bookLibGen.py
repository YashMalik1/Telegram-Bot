from libgen_api import LibgenSearch


def sortYear(el):
    return el["year"]

def sortSize(el):
    return el["size"]

def sortPage(el):
    return el["pages"]

def libgenBook(title):
    """
    Searches the title in libgen and returns the download link and title in a array

    Args:
        title (string): The name of the book
    """

    tf = LibgenSearch()
    print("Starting fetch.... ")
    title_filters = {"Extension": "pdf"}
    titles = tf.search_title_filtered(title, title_filters)

    print("Titles fetched")
    print("Titles fetched")
    
    total_titles = len(titles)
    result = []
    for i in range(total_titles):
        print("\033[A\033[A")
        download_link = tf.resolve_download_links(titles[i])
        if(len(list(download_link.keys())) != 0):
            result.append({
                "title": titles[i]["Title"],
                "year": titles[i]["Year"],
                "pages": titles[i]["Pages"],
                "size": titles[i]["Size"],
                "url": download_link[list(download_link.keys())[1]]
            })
        print(f"Download links {round(100*i/total_titles, 2)}% fetched")

    print("\033[A \033[A")
    print("Download link fetched")

    distinct_title = {}
    for i in range(len(result)):
        if(result[i]["title"] not in distinct_title):
            distinct_title[result[i]["title"].lower()] = []
        distinct_title[result[i]["title"].lower()].append(result[i])
    
    final_result = []
    for el in distinct_title:
        if (len(distinct_title[el]) > 1):
            arr = list(distinct_title[el])
            arr.sort(key=sortYear, reverse=True)
            arr.sort(key=sortSize)
            arr.sort(key=sortPage, reverse=True)
            flag = False
            for el in arr:
                if("Mb" not in el["size"]):
                    flag = True
                    final_result.append(el)
                elif(int(el["size"][0:-2]) < 48):
                    flag = True
                    final_result.append(el)

                if(flag):
                    break
            
            if(flag == False):
                final_result.append(arr[0])

        else:
            final_result.append(distinct_title[el][0])

    return result