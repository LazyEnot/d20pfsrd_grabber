import time


def draw_progress_bar(iterable,
                      prefix="Progress",
                      suffix="Complete",
                      decimals=1,
                      length=100,
                      fill="█",
                      print_end=""
                      ):
    """
    Call in a loop to create terminal progress bar
    @params:
        iterable   - Required  : iterable object (Iterable)
        prefix     - Optional  : prefix string (Str)
        suffix     - Optional  : suffix string (Str)
        decimals   - Optional  : positive number of decimals
                                  in percent complete (Int)
        length     - Optional  : character length of bar (Int)
        fill       - Optional  : bar fill character (Str)
        printEnd   - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    start_time = time.time()
    total = len(iterable)

    # Progress Bar Printing Function
    def print_progress_bar(iteration):
        percent = ("{0:." + str(decimals) + "f}").format(
            100 * (iteration / float(total))
        )
        filled_length = int(length * iteration // total)
        bar = fill * filled_length + '-' * (length - filled_length)
        print(f"\r{prefix} |{bar}| {percent}% ({iteration} of {total}) {suffix}", end=print_end)
    # Initial Call
    print_progress_bar(0)
    # Update Progress Bar
    for i, item in enumerate(iterable):
        yield item
        print_progress_bar(i + 1)
    # Print New Line on Complete
    time_spent = time.time()-start_time
    time_spent = f"{time_spent//60:.0f} minutes and {time_spent%60:.0f} seconds"
    print(f"\nProcess finished in {time_spent}")
