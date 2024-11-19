
comparison_count = 0
past_due_events = []
def quick_sort(array, start, end):
    #Base Case
    if end <= start:
        return
    pivot = partition(array, start, end)
    quick_sort(array, start, pivot - 1)
    quick_sort(array, pivot + 1, end)

def partition(array, start, end):
    global comparison_count, past_due_events  # Declare global to modify it inside the function
    pivot = array[end][1]
    i = start - 1;

    for j in range(start, end):
        comparison_count += 1  # Increment the comparison counter
        if array[j][1] == -101:
            # Move element to excluded list and skip it in sorting
            past_due_events.append(array[j])
        if array[j][1] < pivot:
            i += 1;
            temp = array[i];
            array[i] = array[j];
            array[j] = temp;
    i += 1;
    temp = array[i];
    array[i] = array[end];
    array[end] = temp;
    return i

def get_count():
    return comparison_count