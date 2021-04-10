Pathfinder
==========

> A Python pathfinding visualizer for algorithms such as Dijkstra and A*. Includes drawing, save and load features. 

Table of Contents
=================

<!--ts-->
  * [Features](#features)
  * [Wiki](#wiki)
    * [How to use it](#htu)
    * [How it looks](#hil)
<!--te-->
###

<a name="features"></a>
Features 
========

> ### Implemented and to implement

- [x] Grid Generation
- [x] Dijkstra Algorithm
- [x] A* Algorithm
- [x] Breadth-First Search 
- [x] Depth-First Search
- [x] Grid Saving
- [x] Grid Loading 
- [ ] Code Refactoring

<a name="wiki"></a>
Wiki
====

<a name="htu"></a>
> ### How to use it
- First things first, navigate to the project directory and run the following command in the console: `pip3 install -r requirements.txt`
- Execute `python3 Pathfinder.py`
- Choose a grid size with the `Rows` and `Columns` entries
- Click on the `Build Grid` button to create the grid window
- Draw the source
- Select `Destination` on the `Editing Mode` section
- Draw the destination
- Select `Wall` if you want to draw some walls or `Erase` if you want to erase some walls
- Select the algorithm you want to test
- Click on the `Find Path` button to start the algorithm
<a name="hil"></a>
> ### How it looks
> #### Path found with Dijkstra:
![Dijkstra path](https://i.imgur.com/mGpTEWT.png)
> #### Path found with A*:
![A* path](https://i.imgur.com/Vg6liqd.png)
> #### Path found with A* on a 100x100 grid:
![A* path 100x100 grid](https://i.imgur.com/PHEboSc.png)
> #### Path found with A* on a 100x100 grid:
![A* path 30x30_maze Saved Grid](https://i.imgur.com/QdkYmjV.png)

