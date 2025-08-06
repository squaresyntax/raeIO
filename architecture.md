```plaintext
+------------------------------+
|   User Interface / CLI / API |
+-------------+----------------+
              |
+-------------v----------------+
|       Central Agent Loop     |
+------------------------------+
|  - Task Planner              |
|  - Context Manager           |
|  - Critic/Evaluator          |
|  - Command Handler           |
+-----+--------+--------+------+
      |        |        |
      |        |        |
+-----v--+  +--v-----+  +--v------+
|Multi-  |  |Web     |  |Self-    |
|Modal   |  |Inter-  |  |Trainer/ |
|Percep- |  |action  |  |Bug Test |
|tion    |  |Module  |  |Module   |
+-----+--+  +--+-----+  +--+------+
      |        |           |
      v        v           v
+---------------------------------+
|      External Resources         |
| (Web, APIs, DBs, GPU, etc.)     |
+---------------------------------+
```