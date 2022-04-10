---
title: 'pybdshadow: A python package for building shadow analysis'
tags:
  - Python
  - GIS
  - Geospatial data 
  - Sunlight 
  - Urban analysis 
  - Building shadow 
  - Building outline data 
  - Billboard visual area
authors:
  - name: Qing Yu^[corresponding author]
    orcid: 0000-0003-2513-2969
    affiliation: 1
  - name: Ge Li
    orcid: 需补充
    affiliation: 2
affiliations:
 - name: Key Laboratory of Road and Traffic Engineering of the Ministry of Education, Tongji University, 4800 Cao’an Road, Shanghai 201804, People’s Republic of China
   index: 1
 - name: 需补充
   index: 2
date: 30 April 2022
bibliography: paper.bib
---
# Summary

背景，城市数字孪生的趋势出现。

建筑阴影分析潜在的应用有哪些？

建筑轮廓的数据能够获取，为我们分析xx提供了机会

# State of the art

相关研究：
利用阴影数据进行的研究有哪些？分别有什么应用？

计算方法：
已有的阴影计算方法有哪些？有什么工具？

总结：
缺乏一个能够兼容Python数据处理处理体系、且支持向量化快速计算（像pybdshadow这样）的工具

# Statement of need

pybdshadow是什么？有什么用？提供了平行光源与点光源的建筑阴影向量化计算方法，能够xxx。

同时，pybdshadow也提供了基于阴影数据做进一步应用的方法，如广告可视区域计算，广告优化选址等。

目前pybdshadow提供了以下功能：

- *Building Data Preprocess*:

- *建筑阴影计算*: 包括平行光源与点光源

- *广告可视区域分析*: 基于哪篇论文的方法，能够xxx

- *Building 与阴影的可视化*: Built-in visualization capabilities leverage the visualization package `keplergl` to interactively visualize data in Jupyter notebooks with simple code.


The target audience of `pybdshadow` includes: 
1) Data science researchers and data engineers in the field of xxx, xxx, and urban computing, particularly those who want to xxx; 

2) Government, enterprises, or other entities who expect xxx management decision support through xxx spatio-temporal data analysis.

The latest stable release of the software can be installed via `pip` and full documentation
can be found at https://pybdshadow.readthedocs.io/en/latest/.

放三张效果图


# References
