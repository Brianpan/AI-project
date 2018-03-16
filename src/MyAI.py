# ======================================================================
# FILE:        MyAI.py
#
# AUTHOR:      Abdullah Younis
#
# DESCRIPTION: This file contains your agent class, which you will
#              implement. You are responsible for implementing the
#              'getAction' function and any helper methods you feel you
#              need.
#
# NOTES:       - If you are having trouble understanding how the shell
#                works, look at the other parts of the code, as well as
#                the documentation.
#
#              - You are only allowed to make changes to this portion of
#                the code. Any changes to other portions of the code will
#                be lost when the tournament runs your code.
# ======================================================================

from Agent import Agent
from enum import Enum

class MyAI ( Agent ):
    def __init__ ( self ):
        # ======================================================================
        # YOUR CODE BEGINS
        # ======================================================================
        self.discover_cell_count = 0
        self.max_x = 7
        self.max_y = 7

        self.map_status = [[0 for i in range(7)] for j in range(7)]
        self.stench_status = [[MyAI.TrapStatus.UNKNOWN for i in range(7)] for j in range(7)]
        self.breeze_status = [[MyAI.TrapStatus.UNKNOWN for i in range(7)] for j in range(7)]
        self.explore_status = [[0 for i in range(7)] for j in range(7)]

        self.move_candidates = []
        self.current_pos = [0, 0]
        self.prev_pos = None
        self.current_face = MyAI.FaceStatus.RIGHT
        self.is_wumpus = True

        self.is_turnback = False
        self.turn_init = False
        self.turning_move = []
        self.next_turn_move = None
        self.next_position = None
        self.has_arrow = True
        self.last_shoot = False
        # ======================================================================
        # YOUR CODE ENDS
        # ======================================================================

    def getAction( self, stench, breeze, glitter, bump, scream ):
        # ======================================================================
        # YOUR CODE BEGINS
        # ======================================================================
        # return 
        if self.is_turnback and self.current_pos[0] == 0 and  self.current_pos[1] == 0:
            return Agent.Action.CLIMB

        if breeze and self.current_pos[0] == 0 and  self.current_pos[1] == 0:
            return Agent.Action.CLIMB

        if self.last_shoot and not scream and self.current_pos[0] == 0 and  self.current_pos[1] == 0:
            return Agent.Action.CLIMB
        else:
            last_shoot = False

        # update boundary
        if bump:
            self.updateBoundary()

        cur_x = self.current_pos[0]
        cur_y = self.current_pos[1]

        # mark discovered and safe
        self.discover_cell_count += 1  
        self.map_status[cur_x][cur_y] = MyAI.MoveStatus.SAFE
        self.explore_status[cur_x][cur_y] = MyAI.MoveStatus.SAFE

        if glitter:
            self.is_turnback = True
            self.turning_move = []
            return Agent.Action.GRAB

        # check breeze
        if breeze:
            self.breeze_status[cur_x][cur_y] = MyAI.TrapStatus.TRAP
        else:
            self.breeze_status[cur_x][cur_y] = MyAI.TrapStatus.SAFE
            
        # check stench
        if stench:
            self.stench_status[cur_x][cur_y] = MyAI.TrapStatus.TRAP
            
            if self.has_arrow and cur_x == 0 and cur_y == 0:
                self.has_arrow = False
                self.last_shoot = True
                return Agent.Action.SHOOT
        else:
            self.stench_status[cur_x][cur_y] = MyAI.TrapStatus.SAFE
        
        # update neighbor is safe or not
        if not breeze and ((not self.is_wumpus) or (not stench)):
            moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            for m in moves:
                if (cur_x + m[0]) >= 0 and (cur_y + m[1]) >= 0 and (cur_x + m[0]) < self.max_x and (cur_y + m[1]) < self.max_y:
                    new_x = cur_x + m[0]
                    new_y = cur_y + m[1]
                    self.map_status[new_x][new_y] = MyAI.MoveStatus.SAFE
        
        # kill Wumpus or not 
        
        if scream:
            self.is_wumpus = False
        
        # update neighbors are danger or not
        self.updateNeighbors()

        if self.is_turnback is True:
            return self.turnBack()

        # next move AI
        return self.moveAI()

        # ======================================================================
        # YOUR CODE ENDS
        # ======================================================================
    
    # ======================================================================
    # YOUR CODE BEGINS
    # ======================================================================
    class MoveStatus(Enum):
        UNKNOWN = 0
        SAFE    = 1
        DANGER  = -1

    class FaceStatus(Enum):
        RIGHT = 0
        LEFT  = 1
        UP    = 2
        DOWN  = 3

    class TrapStatus(Enum):
        UNKNOWN = 0
        SAFE    = 1
        TRAP    = -1

    def moveAI( self ):
        x, y = self.current_pos[0], self.current_pos[1]

        if not self.turning_move:
            moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            for m in moves:
                if (x + m[0]) >= 0 and (y + m[1]) >= 0 and (x + m[0]) < self.max_x and (y + m[1]) < self.max_y:
                    new_x = x + m[0]
                    new_y = y + m[1]
                    if self.map_status[new_x][new_y] !=  MyAI.MoveStatus.DANGER:
                        self.move_candidates = [[new_x, new_y]] + self.move_candidates
            
            next_move = self.analyzeNextMove()
            if self.is_turnback:
                return self.turnBack()

            self.next_position = next_move
            self.turning_move = self.calculateMoves() 

        next_move = self.turning_move.pop(0)
        
        # update face
        self.updateFace(next_move)

        # update next move position
        if next_move == Agent.Action.FORWARD:
            self.prev_pos = self.current_pos
            if self.current_face == MyAI.FaceStatus.LEFT:
                self.current_pos = [x-1, y]
            elif self.current_face == MyAI.FaceStatus.RIGHT:
                self.current_pos = [x+1, y]
            elif self.current_face == MyAI.FaceStatus.UP:
                self.current_pos = [x, y+1]
            else:
                self.current_pos = [x, y-1]

        return next_move

    # start tp turn back 
    def turnBack( self ):
        if not self.turn_init:
            self.next_position = (0, 0)
            self.turn_init = True
            self.turning_move = self.calculateMoves()
        if len(self.turning_move) > 0:
            next_move = self.turning_move.pop(0)
            return next_move
        else:
            return Agent.Action.CLIMB

    ## update face status ##
    def updateFace( self, move ):
        if move == Agent.Action.TURN_RIGHT:
            if self.current_face == MyAI.FaceStatus.RIGHT:
                self.current_face = MyAI.FaceStatus.DOWN
            elif self.current_face == MyAI.FaceStatus.LEFT:
                self.current_face = MyAI.FaceStatus.UP
            elif self.current_face == MyAI.FaceStatus.UP:
                self.current_face = MyAI.FaceStatus.RIGHT
            else:
                self.current_face = MyAI.FaceStatus.LEFT

        elif move == Agent.Action.TURN_LEFT:
            if self.current_face == MyAI.FaceStatus.RIGHT:
                self.current_face = MyAI.FaceStatus.UP
            elif self.current_face == MyAI.FaceStatus.LEFT:
                self.current_face = MyAI.FaceStatus.DOWN
            elif self.current_face == MyAI.FaceStatus.UP:
                self.current_face = MyAI.FaceStatus.LEFT
            else:
                self.current_face = MyAI.FaceStatus.RIGHT

    def updateBoundary( self ):
        if self.current_face == MyAI.FaceStatus.RIGHT:    
            self.max_x = self.current_pos[0]
            self.current_pos[0] -= 1 
        if self.current_face == MyAI.FaceStatus.UP:
            self.max_y = self.current_pos[1]
            self.current_pos[1] -= 1
        
        # remove candidates which is over the boundary
        new_candidates = []
        for old_c in self.move_candidates:
            x = old_c[0]
            y = old_c[1]
            if x < self.max_x and y < self.max_y:
                new_candidates.append([x, y])

        self.move_candidates = new_candidates

    def isSafe( self, x, y ):
        return self.map_status[x][y] == MyAI.MoveStatus.SAFE
    
    def dist( self, p1, p2 ):
        diff_x = p2[0] - p1[0]
        diff_y = p2[1] - p1[1]
        turn_base = 0
        
        if self.current_face == MyAI.FaceStatus.UP:
            if diff_x != 0:
                turn_base += 1
            if diff_y < 0:
                turn_base += 2
        elif self.current_face == MyAI.FaceStatus.DOWN:
            if diff_x != 0:
                turn_base += 1
            if diff_y > 0:
                turn_base += 2            
        elif self.current_face == MyAI.FaceStatus.RIGHT:
            if diff_x < 0:
                turn_base += 2
            if diff_y != 0:
                turn_base += 1
        else:
            if diff_x > 0:
                turn_base += 2
            if diff_y != 0:
                turn_base += 1

        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]) + turn_base
    
    # analyze next position to move
    def analyzeNextMove( self ):
        x = self.current_pos[0]
        y = self.current_pos[1]
        ranking_list = []
        # remove dup
        self.move_candidates = [list(t) for t in set(tuple(element) for element in self.move_candidates)]

        for candidate in self.move_candidates:
            # skip which is already explored
            if self.explore_status[candidate[0]][candidate[1]] == MyAI.MoveStatus.SAFE:
                continue
            dist = self.dist( (x, y), candidate )
            h = self.hazardRate(candidate[0], candidate[1])
            ranking_list.append( ((h, dist), candidate) )

        ranking_list = sorted(ranking_list, key=lambda x: x[0])

        next_move = ranking_list[0]
        self.move_candidates.remove(next_move[1])

        # too dangerous
        if next_move[0][0] > 0:
            self.is_turnback = True

        return next_move[1]

    def hazardRate( self, x, y ):
        moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        total_neighbors = 0
        neighbor_stench = 0
        neighbor_breeze = 0

        # is safe no danger
        if self.isSafe(x, y):
            return -1

        for m in moves:
            cx = x+m[0] 
            cy = y+m[1]
            if cx >= 0 and cx < self.max_x and cy >= 0 and cy < self.max_y:
                total_neighbors += 1
                # still have wampus
                if self.is_wumpus:
                    if self.stench_status[cx][cy] == MyAI.TrapStatus.TRAP:
                        neighbor_stench += 1
                    elif self.stench_status[cx][cy] == MyAI.TrapStatus.UNKNOWN:
                        neighbor_stench += 0.25

                if self.breeze_status[cx][cy] == MyAI.TrapStatus.TRAP:
                    neighbor_stench += 1
                elif self.breeze_status[cx][cy] == MyAI.TrapStatus.UNKNOWN:
                    neighbor_stench += 0.25

        hazards = max(neighbor_stench, neighbor_breeze)/total_neighbors

        return hazards

    # move from one cell to another one
    def generatePath(self, parent, dest_position, start_position):
        position_list = [dest_position]
        key = dest_position
        
        while parent[key] != start_position:
            position_list.append(parent[key])
            key = parent[key]

        return position_list[::-1]
    
    def getPointMoves( self, cur_x, cur_y, dest_x, dest_y):
        moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        queue = [(cur_x, cur_y)]
        parent = {}
        visited = {}

        while queue:
            pt = queue.pop(0)
            x = pt[0]
            y = pt[1]
            for m in moves:
                cx = x+m[0] 
                cy = y+m[1]
                # check visited
                if visited.get((cx,cy), False):
                    continue
                visited[(cx, cy)] = True

                if cx >= 0 and cx < self.max_x and cy >= 0 and cy < self.max_y and self.map_status[cx][cy] == MyAI.MoveStatus.SAFE:
                    parent[(cx, cy)] = (x, y)
                    queue.append((cx, cy))

                    if (cx == dest_x) and (cy == dest_y):
                        dest_position = (dest_x, dest_y)
                        
                        return self.generatePath(parent, dest_position, (cur_x, cur_y))

    def calculateMoves( self ):
        x = self.current_pos[0]
        y = self.current_pos[1]
        dest_x = self.next_position[0]
        dest_y = self.next_position[1]
        c_face = self.current_face

        move_list = []

        move_pts = self.getPointMoves(x, y, dest_x, dest_y)
        for next_move in move_pts:
            move_list += self.stepMove(x, y, next_move[0], next_move[1], c_face)
            # update face status
            if next_move[0] - x == 1:
                c_face = MyAI.FaceStatus.RIGHT
                x += 1
            elif next_move[0] - x == -1:
                c_face = MyAI.FaceStatus.LEFT
                x -= 1
            elif next_move[1] - y == 1:
                c_face = MyAI.FaceStatus.UP
                y += 1
            else:
                c_face = MyAI.FaceStatus.DOWN
                y -= 1

        return move_list

    # move to next position's robot movement
    def stepMove( self, x, y, nx, ny, c_face ):
        moves = []

        if nx - x == 1:
            if c_face == MyAI.FaceStatus.RIGHT:
                moves = [Agent.Action.FORWARD]
            elif c_face == MyAI.FaceStatus.LEFT:
                moves = [Agent.Action.TURN_RIGHT, Agent.Action.TURN_RIGHT, Agent.Action.FORWARD]
            elif c_face == MyAI.FaceStatus.UP:
                moves = [Agent.Action.TURN_RIGHT, Agent.Action.FORWARD]
            else:
                moves = [Agent.Action.TURN_LEFT, Agent.Action.FORWARD]
        elif nx - x == -1:
            if c_face == MyAI.FaceStatus.LEFT:
                moves = [Agent.Action.FORWARD]
            elif c_face == MyAI.FaceStatus.RIGHT:
                moves = [Agent.Action.TURN_RIGHT, Agent.Action.TURN_RIGHT, Agent.Action.FORWARD]
            elif c_face == MyAI.FaceStatus.DOWN:
                moves = [Agent.Action.TURN_RIGHT, Agent.Action.FORWARD]
            else:
                moves = [Agent.Action.TURN_LEFT, Agent.Action.FORWARD]
        elif ny - y == 1:
            if c_face == MyAI.FaceStatus.LEFT:
                moves = [Agent.Action.TURN_RIGHT, Agent.Action.FORWARD]
            elif c_face == MyAI.FaceStatus.RIGHT:
                moves = [Agent.Action.TURN_LEFT, Agent.Action.FORWARD]
            elif c_face == MyAI.FaceStatus.DOWN:
                moves = [Agent.Action.TURN_RIGHT, Agent.Action.TURN_RIGHT, Agent.Action.FORWARD]
            else:
                moves = [Agent.Action.FORWARD]
        else:
            if c_face == MyAI.FaceStatus.RIGHT:
                moves = [Agent.Action.TURN_RIGHT, Agent.Action.FORWARD]
            elif c_face == MyAI.FaceStatus.LEFT:
                moves = [Agent.Action.TURN_LEFT, Agent.Action.FORWARD]
            elif c_face == MyAI.FaceStatus.UP:
                moves = [Agent.Action.TURN_RIGHT, Agent.Action.TURN_RIGHT, Agent.Action.FORWARD]
            else:
                moves = [Agent.Action.FORWARD]

        return moves

    def updateNeighbors(self):
        x, y = self.current_pos[0], self.current_pos[1]
        moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for m in moves:
            cx = x+m[0] 
            cy = y+m[1]
            if cx >= 0 and cx < self.max_x and cy >= 0 and cy < self.max_y:
                if self.breeze_status[cx][cy] == MyAI.TrapStatus.TRAP:
                    evd_list = []
                    safePt, totalPt = 0, 0
                    for m2 in moves:
                        cx2 = cx + m2[0]
                        cy2 = cy + m2[1] 
                        if cx2 >= 0 and cx2 < self.max_x and cy2 >= 0 and cy2 < self.max_y and cx2 != x and cy2 != y: 
                            totalPt += 1
                            if self.map_status[cx2][cy2] == MyAI.MoveStatus.SAFE:
                                safePt += 1
                                continue
                            evd_list.append((cx2, cy2))
                    
                    if totalPt - safePt == 1:
                        self.map_status[evd_list[0][0]][evd_list[0][1]] = MyAI.MoveStatus.DANGER
                
                if self.breeze_status[x][y] == MyAI.TrapStatus.SAFE and self.is_wumpus == False:
                    self.map_status[cx][cy] = MyAI.MoveStatus.SAFE

    # ======================================================================
    # YOUR CODE ENDS
    # ======================================================================