详细的在文档：D:\agent\graphrag\graphrag\thy_test\02_test_Neo4j\3. Microsoft GraphRAG 自定义接入图数据库 Neo4j.ipynb 

(1)
在cmd中：
查看java版本，java -version，要求`Java`版本是`OpenJDK`的`21`版本

（2）
在`cmd`命令行中输入`neo4j windows-service install`，然后回车，如果出现`Neo4j`服务安装成功的信息，则说明`Neo4j`服务安装成功。

************安装完成后*************
(3)
在`cmd`命令行中输入`neo4j.bat console`，然后回车，如果出现`Neo4j`服务启动成功的信息，则说明`Neo4j`服务启动成功。

(4)
启动后会看到两个连接地址，一个是`Bolt:localhost:7687`，一个是`HTTP:localhost:7474`，其中`Bolt`是`Neo4j`的`Bolt`协议连接地址，`HTTP`是`Neo4j`的`HTTP`协议连接地址。我们可以通过`localhost:7474`访问`Neo4j`的`Web`界面


（5）清空数据库
在 http://localhost:7474 中 执行 
MATCH (n) DETACH DELETE n;
刷新Schema缓存：:schema

// 检查节点总数
MATCH (n) RETURN count(n) AS total_nodes;

// 检查每个标签的节点数
CALL db.labels() YIELD label
CALL apoc.cypher.run('MATCH (n:' + label + ') RETURN count(n) as count', {}) YIELD value
RETURN label, value.count as node_count;



（6）
检查Neo4j状态：
        # 检查Neo4j服务状态
        neo4j.bat status
如果需要重启Neo4j：
        # 停止Neo4j服务
        neo4j.bat stop

        # 等待几秒钟确保完全停止
        timeout /t 5

        # 重新启动控制台模式
        neo4j.bat console
如果需要以服务模式运行：
        # 停止当前运行的Neo4j
        neo4j.bat stop

        # 以服务模式启动（后台运行）
        neo4j.bat start
查看详细信息：
        neo4j.bat console --verbose

常用Neo4j命令：
        # 查看状态
        neo4j.bat status

        # 启动服务（后台运行）
        neo4j.bat start

        # 停止服务
        neo4j.bat stop

        # 重启服务
        neo4j.bat restart

        # 控制台模式启动（前台运行，可以看到日志）
        neo4j.bat console




