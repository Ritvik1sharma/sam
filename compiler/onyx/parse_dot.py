import pydot

class SAMDotGraph():

    def __init__(self, filename=None) -> None:
        assert filename is not None, "filename is None"
        self.graphs = pydot.graph_from_dot_file(filename)
        self.graph = self.graphs[0]
        self.mapped_graph = {}
        print(self.graph)
        self.nodes = self.graph.get_nodes()
        self.edges = self.graph.get_edges()
        print(self.nodes)
        for node in self.nodes:
            # Map the
            attrs = node.get_attributes()

            print(node.get_name())
            print(node.get_comment())
            node_type = node.get_comment()
        self.rewrite_lookup()
        self.rewrite_arrays()


    def rewrite_lookup(self):
        '''
        Rewrites the lookup nodes to become (wr_scan, rd_scan, buffet) triples
        '''
        for node in self.graph.get_nodes():
            if node.get_name().contains('fiber-lookup'):
                # Rewrite this node to a read
                root = node.get_name().contains('root')
                attrs = node.get_attributes()
                rd_scan = pydot.Node("rd_scan", attrs=attrs)
                wr_scan = pydot.Node("wr_scan", attrs=attrs)
                buffet = pydot.Node("buffet", attrs=attrs)
                glb_write = pydot.Node("glb_write", attrs=attrs)
                crd_out_edge = [edge for edge in self.edges if edge.get_label() == "crd" and edge.get_source() == node][0]
                ref_out_edge = [edge for edge in self.edges if edge.get_label() == "ref" and edge.get_source() == node][0]
                ref_in_edge = None
                if not root:
                    # Then we have ref in edge...
                    ref_in_edge = [edge for edge in self.edges if edge.get_label() == "ref" and edge.get_destination() == node][0]
                # Now add the nodes and move the edges...
                self.graph.add_node(rd_scan)
                self.graph.add_node(wr_scan)
                self.graph.add_node(buffet)
                self.graph.add_node(glb_write)
                # Glb to WR
                glb_to_wr = pydot.Edge(src=glb_write, dst=wr_scan, label="glb_to_wr", style="bold")
                self.graph.add_edge(glb_to_wr)
                # write + read to buffet
                wr_to_buff = pydot.Edge(src=wr_scan, dst=buffet, label='wr_to_buff')
                self.graph.add_edge(wr_to_buff)
                rd_to_buff = pydot.Edge(src=rd_scan, dst=buffet, label='rd_to_buff')
                self.graph.add_edge(rd_to_buff)
                # Now inject the read scanner to other nodes...
                rd_to_down_crd = pydot.Edge(src=rd_scan, dst=crd_out_edge.get_destination(), attrs=crd_out_edge.get_attributes())
                rd_to_down_ref = pydot.Edge(src=rd_scan, dst=ref_out_edge.get_destination(), attrs=ref_out_edge.get_attributes())
                self.graph.add_edge(rd_to_down_crd)
                self.graph.add_edge(rd_to_down_ref)
                if ref_in_edge is not None:
                    up_to_ref = pydot.Edge(src=ref_in_edge.get_source(), dst=rd_scan, attrs=ref_in_edge.get_attributes())
                    self.graph.add_edge(up_to_ref)

            elif node.get_name().contains('fiber-write'):
                # Rewrite this node to a write
                pass


if __name__ == "__main__":
    matmul_dot = "/home/max/Documents/SPARSE/sam/compiler/sam-outputs/dot/" + "matmul_ijk.gv"
    SAMDotGraph(filename=matmul_dot)