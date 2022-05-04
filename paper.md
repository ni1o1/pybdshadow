---
title: 'pybdshadow: A python package for building shadow calculation, analysis and visualization'
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
    orcid: 0000-0002-5761-7269
    affiliation: 2
affiliations:
 - name: Key Laboratory of Road and Traffic Engineering of the Ministry of Education, Tongji University, 4800 Cao’an Road, Shanghai 201804, People’s Republic of China
   index: 1
 - name: School of Geography and Information Engineering, China University of Geosciences (Wuhan), Wuhan 430074, People’s Republic of China
   index: 2
date: 30 April 2022
bibliography: paper.bib
---
# Summary

背景，城市数字孪生的趋势出现。

建筑阴影分析潜在的应用有哪些？

建筑轮廓的数据能够获取，为我们分析xx提供了机会
数字时代，互联网技术的革新催生了“数字孪生城市”（DT）趋势的出现[@9267879-1]。 “数字孪生城市”的广泛应用又同时促进了相关领域的发展[@9254288-2]。而对城市的研究绕不开城市的主体组件——建筑物，研究表明，建筑物阴影对城区局部地表温度存在一定的影响[@DAI201977-3]，并进一步作用于城市热岛[@PARK2021101655-4]；近些年开始飞速发展的光伏新能源发电也受到建筑物遮光的影响，建筑的阴影会降低光伏系统的生电效率[@WU2021116884-5]，同时，研究建筑物阴影分布有利于寻找最佳的光伏板位置[@YADAV201811-6]，实现最大收益的光能利用。
阴影可以作为环境的一部分对其产生影响，另一方面，建筑阴影也可以作为建筑的一种属性还原城市环境中的建筑物[7]；此外，建筑物阴影也在城市区域规划[8]、噪声传播（广义阴影）[@bolin2020investigation-9]、灾后建筑重建等方面有着重要的作用。而随着摄影测量及深度学习等技术的发展，建筑轮廓数据的快速且便利地获取[?]为我们分析在光照作用下的阴影位置提供了机会。

# State of the art

相关研究：
利用阴影数据进行的研究有哪些？分别有什么应用？

计算方法：
已有的阴影计算方法有哪些？有什么工具？

总结：
缺乏一个能够兼容Python数据处理处理体系、且支持向量化快速计算（像pybdshadow这样）的工具

在遥感及图像处理领域，研究者们通过光谱信息结合空间信息处理建筑物等阴影造成的信息缺失或损耗。通常的研究手段是将建筑阴影与其它地物类型分离，其本质还是二维的图像分类。
(Guoqing Zhou)的文章提出了一种将二维的图像处理与三维的建筑投影结合的方法（DBM）获取图像中的建筑阴影[@zhou2015integrated-10][@rs12040679-11]，[@RAFIEE2014397-12]开发出一种基于建筑信息模型（BIM）与地理信息系统（GIS）的建筑阴影分析脚本用于分析室内光照；[@HONG2016408-13]利用经典的阴影分析法Hillshade计算可用的屋顶光伏面积。Fabio Miranda等人利用光线追踪阴影技术计算长时间的阴影累计[@8283638-14]，然而光线追踪虽然能获得符合人眼视觉的漂亮真实的阴影效果，但是无法获取阴影区域坐标进行机理层面的分析。
ArcGIS中的Hillshade工具可以进行栅格数据的阴影检测，而在实际应用中，建筑物通常以矢量形式存储，存储形式的转变往往会伴随着信息的损失。
因此，目前为止，针对建筑物阴影的研究虽然较多，但是缺乏一个能够兼容Python数据处理处理体系、且支持向量化快速计算（像pybdshadow这样）的工具。

# Statement of need

pybdshadow是什么？有什么用？提供了平行光源与点光源的建筑阴影向量化计算方法，能够xxx。

同时，pybdshadow也提供了基于阴影数据做进一步应用的方法，如广告可视区域计算，广告优化选址等。

目前pybdshadow提供了以下功能：

- *Building Data Preprocess*:
- *建筑阴影计算*: 包括平行光源与点光源
- *Building 与阴影的可视化*: Built-in visualization capabilities leverage the visualization package `keplergl` to interactively visualize data in Jupyter notebooks with simple code.

The target audience of `pybdshadow` includes:

1) Data science researchers and data engineers in the field of xxx, xxx, and urban computing, particularly those who want to xxx;
2) Government, enterprises, or other entities who expect xxx management decision support through xxx spatio-temporal data analysis.

pybdshadow是一个可以对大数据矢量类型的建筑物进行阴影计算的库，提供了平行光源与点光源的建筑阴影向量化计算方法，针对地理矢量建筑数据在不同光源类型及光源位置下的阴影分析及显示。实现数据处理、阴影计算、可视化的集成效果。
目前pybdshadow提供了以下功能：
•	Building Data Preprocess:将用户输入的数据处理成所需要的geopandas格式。
•	建筑阴影计算: 包括平行光源与点光源
•	平行光源：根据用户输入的经纬度及时间利用suncalc库计算太阳方位角及高度角，利用太阳角度信息推算阴影位置。
•	点光源：用户输入一个三维坐标，计算在该点光源下的投影
•	Building 与阴影的可视化: Built-in visualization capabilities leverage the visualization package keplergl to interactively visualize data in Jupyter notebooks with simple code.(\autoref{fig:fig1})

(\autoref{fig:fig2})

The target audience of `pybdshadow` includes:

1. Data science researchers and data engineers in the field of xxx, xxx, and urban computing, particularly those who want to xxx;
2. Government, enterprises, or other entities who expect xxx management decision support through xxx spatio-temporal data analysis.

The latest stable release of the software can be installed via `pip` and full documentation can be found at https://pybdshadow.readthedocs.io/en/latest/.

![pybdshadow</code></code></code></code></code></code></code></code></code></code></code></code></code></code></code></code></code></code></code></code></code></code></code></code></code></code></code></code></code></code></code></code> generates and visualize building shadows.\label{fig:fig1}](image/paper/1651656857394.png){ width=100% }

![pybdshadow</code></code></code></code></code></code></code></code></code></code></code></code></code></code></code></code></code></code></code></code></code></code></code></code></code></code></code></code></code></code></code></code> analyse sunshine time both on the roof and on the ground.\label{fig:fig2}](image/paper/1651656639873.png){ width=100% }

# References

[1] Digital Twin of City: Concept Overview
[2] Digital Transformation Revolution with Digital Twin Technology
[3] Dai, Z., Guldmann, J. M., & Hu, Y. (2019). Thermal impacts of greenery, water, and impervious structures in Beijing’s Olympic area: A spatial regression approach. Ecological Indicators, 97, 77–88
[4] Impacts of tree and building shades on the urban heat island: Combining remote sensing, 3D digital city and spatial regression approaches
[5] Coupled optical-electrical-thermal analysis of a semi-transparent photovoltaic glazing façade under building shadow
[6] Performance of building integrated photovoltaic thermal system with PV 1 module installed at optimum tilt angle and influenced by shadow
[7] Introduction of the mean shift algorithm in SAR imagery: Application to shadow extraction for building reconstruction
[8] ANALYSIS OF BUILDING SHADOW IN URBAN PLANNING: A REVIEW
[9] An investigation of the influence of the refractive shadow zone on wind turbine noise
ürker, M.; Sümer, E. Building-based damage detection due to earthquake using the watershed segmentation
of the post-event aerial images. Int. J. Remote Sens. 2008, 29, 3073–3089. [CrossRef]
[10] An integrated approach for shadow detection of the building in urban areas
[11] Building Shadow Detection on Ghost Images
[12] From BIM to geo-analysis: view coverage and shadow analysis by BIM/GIS integration
[13] Estimation of the available rooftop area for installing the rooftop solar photovoltaic (PV) system by analyzing the building shadow using Hillshade analysis
[13] Three-Dimensional Rule-Based City Modelling to Support Urban Redevelopment Process
[14] Shadow Accrual Maps: Efficient Accumulation of City-Scale Shadows Over Time
