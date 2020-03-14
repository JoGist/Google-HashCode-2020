import sys
from typing import List, Dict
import heapq


def parse_dataset(input_path: str, output_path: str) -> (int, int, int, List[int], List[Dict[str, int]], List[List[int]], List[bool]):
    """
    Parses the input dataset.

    @param input_path: path to dataset
    @param output_path: path to output file

    @return:
        number of books,
        number of libraries,
        deadline in terms of days
        scores per book (as a List)
        information about libraries (as a List of Dict)
        books per library (as a List)
        duplicate books (as a List of bool)
    """

    num_books = 0
    num_libraries = 0
    num_days=0
    book_score = []
    libraries_info = []
    books_per_library = []

    # dataset parsing
    with open(input_path, 'r') as dataset:
        first = True
        second = False

        count = -1
        for line in dataset:
            # load general info
            if(count == -1 and first):
                first = False
                second = True

                line = line.strip("\n").split(" ")
                num_books = int(line[0])
                num_libraries = int(line[1])
                num_days = int(line[2])
            elif(count == -1 and second):
                second = False
                book_score = [int(v) for v in line.strip("\n").split(" ")]
                count = 0
                first = True

            # process each library's info
            else:
                try:
                    if(first):
                        first = False
                        second = True
                        line = line.strip("\n").split(" ")
                        libraries_info.append({"num_books": int(line[0]),
                                                "signup": int(line[1]),
                                                "ship_rate": int(line[2])})
                    elif(second):
                        second = False
                        first = True
                        curr_books = [int(v) for v in line.strip("\n").split(" ")]
                        curr_scores = {}
                        for book in curr_books:
                            curr_scores[book] = book_score[book]
                        
                        del curr_books
                        sorted_scores = {k: v for k, v in sorted(curr_scores.items(), key=lambda item: item[1], reverse=True)}
                        del curr_scores
                        #TO DO
                        #
                        #if book already in library don't append
                        books_per_library.append([k for k, v in sorted_scores.items()])
                except ValueError:
                    continue

    already_sent_book = [False] * num_books

    return num_books, num_libraries, num_days, book_score, libraries_info, books_per_library, already_sent_book

def adaptive_scores(num_books: int, num_libraries: int, book_score: List[int],
                    libraries_info: List[Dict[str, int]], books_per_library: List[List[int]],
                    library_signup: List[bool], already_sent_books: List[bool], remaining_days: int) -> List[float]:
    
    library_score = [0] * num_libraries
    for i in range(num_libraries):
        if library_signup[i]:
            continue
        #print(books_per_library,book_score,already_sent_books)
        if(remaining_days<=libraries_info[i]["signup"]): curr_score=0
        else:
            lib_book=libraries_info[i]["num_books"] 
            total_value = sum([book_score[j] if not already_sent_books[j] else 0 for j in books_per_library[i]])
            curr_score = float( (total_value) * (libraries_info[i]["ship_rate"]+lib_book)**2 ) 
            curr_score /= ( (lib_book - lib_book/remaining_days) + (libraries_info[i]["signup"])**2)
        library_score[i] = curr_score
    
    return library_score

def adaptive_solution(num_books: int, num_libraries: int, num_days: int,
                      book_score: List[int], libraries_info: List[Dict[str, int]],
                      books_per_library: List[List[int]], already_sent_books: List[bool]):

    # list of libraries, ordered
    solution_libraries = []

    # list of books per library, ordered
    solution_books = []

    library_signup = [False] * num_libraries
    
    next_deadline = 0
    for day in range(num_days):
        # only signup new libraries once the previous one has done it
        if day == next_deadline:
            library_scores = adaptive_scores(num_books=num_books,
                                             num_libraries=num_libraries,
                                             book_score=book_score,
                                             libraries_info=libraries_info,
                                             books_per_library=books_per_library,
                                             library_signup=library_signup,
                                             already_sent_books=already_sent_books,
                                             remaining_days=num_days - day )
            #print(library_scores)
            best_score = -1
            try:
                libr_scores = [-score for score in library_scores]
                heapq.heapify(libr_scores)
                best_score = -heapq.heappop(libr_scores)
            except IndexError:
                break

            best_library = -1

            # find best library and mark it for signup
            for i in range(num_libraries):
                if not library_signup:
                    continue

                if library_scores[i] == best_score:
                    library_signup[i] = True
                    best_library = i
                    break
            
            curr_books = []
            for book in books_per_library[best_library]:
                if not already_sent_books[book]:
                    curr_books.append(book)
                    already_sent_books[book] = True

            if(len(curr_books) > 0):
                next_deadline += libraries_info[best_library]["signup"]
                solution_books.append(curr_books)
                solution_libraries.append(best_library)

    return solution_libraries, solution_books


def write_solution(solution_libraries: List[int], solution_books: List[List[int]], output_path: str):
    with open(output_path, 'w') as sol:
        sol.write("{l}\n".format(l=len(solution_libraries)))
        for index, library in enumerate(solution_libraries):
            curr_books = [str(book) for book in solution_books[index]]
            sol.write("{l} {books}\n".format(l=library, books=len(curr_books)))
            sol.write("{books}\n".format(books=" ".join(curr_books)))
            sol.flush()

if __name__ == "__main__":
    if(len(sys.argv) != 3):
        print("Usage: solution.py <input path> <output path>")
        sys.exit(-1)
    
    books, libraries, days, scores, libr_info, books_per_libr, duplicates = parse_dataset(input_path=sys.argv[1], output_path=sys.argv[2])

    libr_sol, books_sol = adaptive_solution(num_books=books, num_libraries=libraries, num_days=days, book_score=scores, libraries_info=libr_info, books_per_library=books_per_libr, already_sent_books=duplicates)

    write_solution(solution_libraries=libr_sol, solution_books=books_sol, output_path=sys.argv[2])

#                                   #
#                  __               #
#              ___( o)>             #
#              \ <_. )              #
#               `---'               #
#                                   #
