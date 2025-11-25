from collections import deque
import heapq
import unittest

# Stack for ticket cancellations (LIFO)
class Stack:
    def __init__(self):
        self.stack = []
    
    def push(self, item):
        if not isinstance(item, str) or not item:
            raise ValueError("Invalid ticket ID: Must be a non-empty string")
        if item in self.stack:
            raise ValueError(f"Duplicate ticket ID: {item}")
        self.stack.append(item)
    
    def pop(self):
        if self.is_empty():
            raise Exception("Stack Underflow: No tickets to cancel")
        return self.stack.pop()
    
    def peek(self):
        if self.is_empty():
            return None
        return self.stack[-1]
    
    def is_empty(self):
        return len(self.stack) == 0

# Queue for passenger service (FIFO)
class Queue:
    def __init__(self):
        self.queue = deque()
    
    def enqueue(self, item):
        if not isinstance(item, str) or not item:
            raise ValueError("Invalid passenger ID: Must be a non-empty string")
        self.queue.append(item)
    
    def dequeue(self):
        if self.is_empty():
            raise Exception("Queue Underflow: No passengers to serve")
        return self.queue.popleft()
    
    def is_empty(self):
        return len(self.queue) == 0

# Sorting algorithms for booking data
def bubble_sort(bookings):
    n = len(bookings)
    for i in range(n):
        for j in range(0, n-i-1):
            if bookings[j] > bookings[j+1]:
                bookings[j], bookings[j+1] = bookings[j+1], bookings[j]
    return bookings

def merge_sort(bookings):
    if len(bookings) <= 1:
        return bookings
    mid = len(bookings) // 2
    left = merge_sort(bookings[:mid])
    right = merge_sort(bookings[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

# Dijkstra’s Algorithm for shortest path
def dijkstra(graph, start):
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0
    pq = [(0, start)]
    while pq:
        current_distance, current_node = heapq.heappop(pq)
        if current_distance > distances[current_node]:
            continue
        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(pq, (distance, neighbor))
    return distances

# Floyd-Warshall Algorithm for all-pairs shortest paths
def floyd_warshall(graph):
    nodes = graph.keys()
    dist = {i: {j: float('infinity') for j in nodes} for i in nodes}
    for node in nodes:
        dist[node][node] = 0
        for neighbor, weight in graph[node].items():
            dist[node][neighbor] = weight
    for k in nodes:
        for i in nodes:
            for j in nodes:
                if dist[i][j] > dist[i][k] + dist[k][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    return dist

# Command-line interface for SmartRide
def main():
    ticket_stack = Stack()
    ticket_queue = Queue()
    graph = {
        'A': {'B': 2, 'C': 4},
        'B': {'D': 3},
        'C': {'D': 1},
        'D': {}
    }
    
    while True:
        print("\nSmartRide Ticket Booking System")
        print("1. Book Ticket (Push to Stack)")
        print("2. Cancel Ticket (Pop from Stack)")
        print("3. Add Passenger to Queue")
        print("4. Serve Passenger (Dequeue)")
        print("5. Sort Bookings (Bubble Sort)")
        print("6. Sort Bookings (Merge Sort)")
        print("7. Compute Shortest Path (Dijkstra)")
        print("8. Compute All-Pairs Shortest Paths (Floyd-Warshall)")
        print("9. Exit")
        choice = input("Enter choice (1-9): ")
        
        try:
            if choice == '1':
                ticket_id = input("Enter ticket ID: ")
                ticket_stack.push(ticket_id)
                print(f"Ticket {ticket_id} booked")
            elif choice == '2':
                cancelled = ticket_stack.pop()
                print(f"Cancelled: {cancelled}")
            elif choice == '3':
                passenger_id = input("Enter passenger ID: ")
                ticket_queue.enqueue(passenger_id)
                print(f"Passenger {passenger_id} added to queue")
            elif choice == '4':
                served = ticket_queue.dequeue()
                print(f"Served: {served}")
            elif choice == '5':
                bookings = input("Enter bookings (comma-separated): ").split(',')
                bookings = [b.strip() for b in bookings]
                print("Bubble Sorted:", bubble_sort(bookings.copy()))
            elif choice == '6':
                bookings = input("Enter bookings (comma-separated): ").split(',')
                bookings = [b.strip() for b in bookings]
                print("Merge Sorted:", merge_sort(bookings.copy()))
            elif choice == '7':
                start = input("Enter starting stop (e.g., A): ")
                if start not in graph:
                    raise ValueError("Invalid stop")
                print("Shortest paths:", dijkstra(graph, start))
            elif choice == '8':
                print("All-pairs shortest paths:", floyd_warshall(graph))
            elif choice == '9':
                print("Exiting SmartRide")
                break
            else:
                print("Invalid choice")
        except Exception as e:
            print(f"Error: {e}")

# Test cases
class TestTicketSystem(unittest.TestCase):
    def test_stack_operations(self):
        s = Stack()
        s.push("Ticket1")
        s.push("Ticket2")
        self.assertEqual(s.pop(), "Ticket2")
        self.assertEqual(s.pop(), "Ticket1")
        self.assertRaises(Exception, s.pop)
        self.assertRaises(ValueError, s.push, "")
        self.assertRaises(ValueError, lambda: s.push("Ticket1") or s.push("Ticket1"))
    
    def test_queue_operations(self):
        q = Queue()
        q.enqueue("Passenger1")
        q.enqueue("Passenger2")
        self.assertEqual(q.dequeue(), "Passenger1")
        self.assertEqual(q.dequeue(), "Passenger2")
        self.assertRaises(Exception, q.dequeue)
        self.assertRaises(ValueError, q.enqueue, "")
    
    def test_bubble_sort(self):
        bookings = ["Passenger3", "Passenger1", "Passenger2"]
        sorted_bookings = bubble_sort(bookings.copy())
        self.assertEqual(sorted_bookings, ["Passenger1", "Passenger2", "Passenger3"])
    
    def test_merge_sort(self):
        bookings = ["Passenger3", "Passenger1", "Passenger2"]
        sorted_bookings = merge_sort(bookings.copy())
        self.assertEqual(sorted_bookings, ["Passenger1", "Passenger2", "Passenger3"])
    
    def test_dijkstra(self):
        graph = {'A': {'B': 2, 'C': 4}, 'B': {'D': 3}, 'C': {'D': 1}, 'D': {}}
        self.assertEqual(dijkstra(graph, 'A'), {'A': 0, 'B': 2, 'C': 4, 'D': 5})
    
    def test_floyd_warshall(self):
        graph = {'A': {'B': 2, 'C': 4}, 'B': {'D': 3}, 'C': {'D': 1}, 'D': {}}
        result = floyd_warshall(graph)
        self.assertEqual(result['A']['D'], 5)
        self.assertEqual(result['B']['D'], 3)
        self.assertEqual(result['C']['D'], 1)

if __name__ == "__main__":
    # Run CLI
    main()
    # Run unit tests
    unittest.main(argv=[''], exit=False)