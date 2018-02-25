# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from logging import getLogger

from conda.models.dag import PrefixDag, PrefixDag2
from conda.models.match_spec import MatchSpec
from conda.resolve import dashlist
from tests.core.test_solve import get_solver_2, get_solver_4

log = getLogger(__name__)






def test_prefix_dag_2():
    specs = MatchSpec("conda"), MatchSpec("conda-build"), MatchSpec("intel-openmp"),
    with get_solver_4(specs) as solver:
        final_state = solver.solve_final_state()
        dag = PrefixDag2(final_state, specs)

        # for rec in dag.graph:
        #     print(rec.dist_str(), dashlist((d.dist_str() for d in dag.graph[rec])))
        #     print()
        #
        # for rec, specs in dag.spec_matches.items():
        #     if specs:
        #         print(rec.dist_str(), dashlist((s for s in specs)))
        #         print()
        #


        nodes = dag.topological_sort()
        anchor_node = nodes[20]

        print("node", anchor_node.dist_str())

        print("nodes", dashlist((rec.dist_str() for rec in nodes)))

        print("downstreams", dashlist((rec.dist_str() for rec in dag.downstream(anchor_node))))
        print("all downstreams", dashlist((rec.dist_str() for rec in dag.all_downstreams(anchor_node))))


        print("all roots", dashlist((rec.dist_str() for rec in dag.all_roots())))

        print("all orphans", dashlist((rec.dist_str() for rec in dag.all_orphans())))

        print("all leaves", dashlist((rec.dist_str() for rec in dag.all_leaves())))

        print("predecessors", dashlist((rec.dist_str() for rec in dag.predecessors(anchor_node))))
        print("all predecessors", dashlist((rec.dist_str() for rec in dag.all_predecessors(anchor_node))))

        assert 0










def test_ordered_nodes():
    specs = MatchSpec("numpy"),

    with get_solver_2(specs) as solver:
        final_state = solver.solve_final_state()
        dag = PrefixDag(final_state, specs)
        # dag.open_url()
        from_roots = dag.get_nodes_ordered_from_roots()
        from_roots_order = (
            'mkl',
            'openssl',
            'readline',
            'sqlite',
            'tk',
            'xz',
            'zlib',
            'python',
            'numpy',
        )
        assert tuple(n.record.name for n in from_roots) == from_roots_order
        from_leaves = dag.get_nodes_ordered_from_leaves()
        assert tuple(n.record.name for n in from_leaves) == (
            'numpy',
            'mkl',
            'python',
            'openssl',
            'readline',
            'sqlite',
            'tk',
            'xz',
            'zlib',
        )

        leaves_last = dag.order_nodes_from_roots(from_roots)
        assert leaves_last == dag.order_nodes_from_roots(from_leaves)
        assert tuple(n.record.name for n in leaves_last) == from_roots_order


def test_remove_node_and_children_1():
    specs = MatchSpec("pandas"),
    with get_solver_2(specs) as solver:
        final_state = solver.solve_final_state()

        dag = PrefixDag(final_state, specs)
        six_node = next((n for n in dag.nodes if n.record.name == 'six'))
        assert set(n.record.name for n in six_node.all_descendants()) == {
            'pandas',
            'python-dateutil',
        }
        assert set(n.record.name for n in six_node.all_ascendants()) == {
            'openssl',
            'readline',
            'sqlite',
            'tk',
            'xz',
            'zlib',
            'python',
        }
        removed_records = tuple(dag.remove_node_and_children(six_node))
        assert tuple(r.name for r in removed_records) == (
            'pandas',
            'python-dateutil',
            'six',
        )

        dag = PrefixDag(final_state, specs)
        python_node = next((n for n in dag.nodes if n.record.name == 'python'))
        assert set(n.record.name for n in python_node.all_descendants()) == {
            'pandas',
            'pytz',
            'numpy',
            'six',
            'python-dateutil',
        }
        assert set(n.record.name for n in python_node.all_ascendants()) == {
            'openssl',
            'readline',
            'sqlite',
            'tk',
            'xz',
            'zlib',
        }
        removed_records = tuple(dag.remove_node_and_children(python_node))
        assert tuple(r.name for r in removed_records) == (
            'pandas',
            'numpy',
            'pytz',
            'python-dateutil',
            'six',
            'python',
        )


def test_remove_node_and_children_2_constrained_deps():
    specs = MatchSpec("conda"), MatchSpec("conda-build"),
    with get_solver_4(specs) as solver:
        final_state = solver.solve_final_state()

        dag = PrefixDag(final_state, specs)

        print([str(n) for n in dag.nodes])

        # print(dag.dot_repr())
        six_node = next((n for n in dag.nodes if n.record.name == 'six'))
        assert set(n.record.name for n in six_node.all_descendants()) == {
            'pyopenssl',
            'urllib3',
            'requests',
            'conda',
            'cryptography',
            'conda-build',
        }
        assert set(n.record.name for n in six_node.all_ascendants()) == {
            'ca-certificates',
            'libedit',
            'libffi',
            'libgcc-ng',
            'libstdcxx-ng',
            'ncurses',
            'openssl',
            'python',
            'readline',
            'sqlite',
            'tk',
            'xz',
            'zlib',
        }
        removed_records = tuple(dag.remove_node_and_children(six_node))
        assert tuple(r.name for r in removed_records) == (
            'conda-build',
            'conda',
            'requests',
            'urllib3',
            'pyopenssl',
            'cryptography',
            'six',
        )

        dag = PrefixDag(final_state, specs)
        python_node = next((n for n in dag.nodes if n.record.name == 'python'))
        assert set(n.record.name for n in python_node.all_descendants()) == {
            'asn1crypto',
            'beautifulsoup4',
            'certifi',
            'cffi',
            'chardet',
            'conda',
            'conda-build',
            'conda-verify',
            'cryptography',
            'filelock',
            'glob2',
            'idna',
            'jinja2',
            'markupsafe',
            'pkginfo',
            'psutil',
            'pycosat',
            'pycparser',
            'pyopenssl',
            'pysocks',
            'pyyaml',
            'requests',
            'ruamel_yaml',
            'setuptools',
            'six',
            'urllib3'
        }
        assert set(n.record.name for n in python_node.all_ascendants()) == {
            'ca-certificates',
            'libedit',
            'libffi',
            'libgcc-ng',
            'libstdcxx-ng',
            'ncurses',
            'openssl',
            'readline',
            'sqlite',
            'tk',
            'xz',
            'zlib',
        }
        removed_records = tuple(dag.remove_node_and_children(python_node))
        assert tuple(r.name for r in removed_records) == (
            'conda-build',
            'conda-verify',
            'pyyaml',
            'conda',
            'ruamel_yaml',
            'jinja2',
            'markupsafe',
            'psutil',
            'pycosat',
            'requests',
            'urllib3',
            'pyopenssl',
            'cryptography',
            'asn1crypto',
            'beautifulsoup4',
            'setuptools',
            'certifi',
            'chardet',
            'filelock',
            'glob2',
            'idna',
            'pkginfo',
            'cffi',
            'pycparser',
            'pysocks',
            'six',
            'python',
        )

        dag = PrefixDag(final_state, specs)
        python_node = next((n for n in dag.nodes if n.record.name == 'pycosat'))
        assert set(n.record.name for n in python_node.all_descendants()) == {
            'conda',
            'conda-build',
        }
        assert set(n.record.name for n in python_node.all_ascendants()) == {
            'ca-certificates',
            'libedit',
            'libffi',
            'libgcc-ng',
            'libstdcxx-ng',
            'ncurses',
            'openssl',
            'python',
            'readline',
            'sqlite',
            'tk',
            'xz',
            'zlib',
        }
        removed_records = tuple(dag.remove_node_and_children(python_node))
        assert tuple(r.name for r in removed_records) == (
            'conda-build',
            'conda',
            'pycosat',
        )
