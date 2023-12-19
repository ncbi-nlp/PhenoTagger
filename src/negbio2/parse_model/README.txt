Description
    
    This is a self-trained BLLIP reranking parser model. It uses PTB2-WSJ
    sections 2-21 along with 278,192 self-trained sentences from PubMed
    as training and section 24 for tuning.

More details

    Using my division of the GENIA 1.0 trees available from

        http://bllip.cs.brown.edu/download/genia1.0-division-rel1.tar.gz

    I repeated my self-training experiments in McClosky and Charniak
    (ACL 2008) paper using GENIA 1.0 trees as the labeled data. This
    also allowed me to create a GENIA reranker. The results (on the dev
    set from my division) are quite dramatic:

    Model                                               f-score
    -----------------------------------------------------------
    WSJ                                                74.9
    WSJ + WSJ reranker                                 76.8
    WSJ + PubMed (parsed by WSJ) + WSJ reranker        80.7 [1]
    GENIA                                              83.6
    GENIA + WSJ reranker                               84.5
    GENIA + GENIA reranker                             85.7
    GENIA + PubMed (parsed by GENIA) + GENIA reranker  87.6 [2]

    [1] Original self-trained biomedical parsing model (ACL 2008)
    [2] This model (please cite my thesis)

Questions?
    
    Please email me if you have any (dmcc@cs.stanford.edu)

Release history

    1.29.2014   Repackaged as a "unified parsing model" (no changes to
                the actual model parameters), README updated
    6.16.2009   Initial release
