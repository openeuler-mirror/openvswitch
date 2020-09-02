# Spec file for Open vSwitch kernel modules on openEuler version.

# Copyright (C) 2011, 2012, 2018 Nicira, Inc.
#
# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.  This file is offered as-is,
# without warranty of any kind.

#needsrootforbuild

%define kversion        $(uname -r)
%{?kversion:%define kernel %kversion}

Name: openvswitch-kmod
Version: 2.12.0
Release: 2
Summary: Open vSwitch Kernel Modules
License: GPLv2
URL: http://www.openvswitch.org/
Source: openvswitch-%{version}.tar.gz
Patch0: Prepare-for-2.12.1.patch
Patch1: faq-Update-list-of-kernels-supported-by-2.12.patch
Patch2: raft-Free-leaked-json-data.patch
Patch3: ofproto-dpif-Uninitialize-xlate_cache-to-free-resour.patch
Patch4: dpif-netdev-Handle-uninitialized-value-error-for-mat.patch
Patch5: ovs-ofctl-Free-leaked-minimatch.patch
Patch6: trigger-Free-leaked-ovsdb_schema.patch
Patch7: ovsdb-client-Free-ovsdb_schema.patch
Patch8: dns-resolve-Free-struct-ub_result-when-callback-retu.patch
Patch9: ofproto-dpif-Free-leaked-webster.patch
Patch10: db-ctl-base-Free-leaked-ovsdb_datum.patch
Patch11: conntrack-Validate-accessing-of-conntrack-data-in-pk.patch
Patch12: faq-Update-OVS-DPDK-version-table-for-OVS-2.12.patch
Patch13: datapath-compat-Backports-bugfixes-for-nf_conncount.patch
Patch14: stream_ssl-fix-important-memory-leak-in-ssl_connect-.patch
Patch15: Documentation-Fix-security-mailing-list-address.patch
Patch16: conntrack-Fix-check_orig_tuple-Valgrind-false-positi.patch
Patch17: conntrack-Fix-reverse_nat_packet-variable-datatype.patch
Patch18: ovn-Exclude-inport-and-outport-symbol-tables-from-co.patch
Patch19: flow-fix-incorrect-padding-length-checking-in-ipv6_s.patch
Patch20: netdev-dpdk-Fix-padding-info-comment.patch
Patch21: travis-Drop-MD-related-workaround-for-sparse.patch
Patch22: doc-Fix-incorrect-reference-for-dpdk-testpmd.patch
Patch23: ofproto-fix-a-typo-for-ttl-in-dpif_sflow_actions.patch
Patch24: flow-Fix-using-pointer-to-member-of-packed-struct-ic.patch
Patch25: netdev-afxdp-Fix-umem-creation-failure-due-to-uninit.patch
Patch26: netdev-afxdp-Update-memory-locking-limits-unconditio.patch
Patch27: dpif-netlink-Free-leaked-nl_sock.patch
Patch28: ovsdb-server-Don-t-drop-all-connections-on-read-writ.patch
Patch29: tc-Limit-the-max-action-number-to-16.patch
Patch30: lldp-Fix-for-OVS-crashes-when-a-LLDP-enabled-port-is.patch
Patch31: tests-Fix-indentation-in-userspace-packet-type-aware.patch
Patch32: flow-Fix-crash-on-vlan-packets-with-partial-offloadi.patch
Patch33: ovsdb-server-fix-memory-leak-while-converting-databa.patch
Patch34: dpif-netdev-Do-not-mix-recirculation-depth-into-RSS-.patch
Patch35: dpif-netdev-Fix-time-delta-overflow-in-case-of-race-.patch
Patch36: rhel-openvswitch-fedora.spec.in-Fix-output-redirect-.patch
Patch37: lflow.c-Fix-memory-leak-of-lflow_ref_list_node-ref_n.patch
Patch38: Avoid-indeterminate-statistics-in-offload-implementa.patch
Patch39: lib-tc-Fix-flow-dump-for-tunnel-id-equal-zero.patch
Patch40: netdev-dpdk-Fix-flow-control-not-configuring.patch
Patch41: vswitch.xml-Fix-column-for-xdpmode.patch
Patch42: compat-Add-compat-fix-for-old-kernels.patch
Patch43: rhel-Fix-ovs-kmod-manage.sh-that-may-create-invalid-.patch
Patch44: ovsdb-server-fix-memory-leak-while-deleting-zone.patch
Patch45: ovn-Prevent-erroneous-duplicate-IP-address-messages.patch
Patch46: jsonrpc-increase-input-buffer-size-from-512-to-4096.patch
Patch47: ovsdb-raft-Fix-election-timer-parsing-in-snapshot-RP.patch
Patch48: ipf-bail-out-when-ipf-state-is-COMPLETED.patch
Patch49: ofproto-dpif-Allow-IPv6-ND-Extensions-only-if-suppor.patch
Patch50: flow-Fix-IPv6-header-parser-with-partial-offloading.patch
Patch51: ofproto-Fix-crash-on-PACKET_OUT-due-to-recursive-loc.patch
Patch52: dpdk-Use-DPDK-18.11.5-release.patch
Patch53: dp-packet-Fix-clearing-copying-of-memory-layout-flag.patch
Patch54: rhel-Support-RHEL7.7-build-and-packaging.patch
Patch55: ofproto-fix-stack-buffer-overflow.patch
Patch56: sparse-Get-rid-of-obsolete-rte_flow-header.patch
Patch57: ofproto-dpif-xlate-Restore-table-ID-on-error-in-xlat.patch
Patch58: ovn-controller-Add-missing-port-group-lflow-referenc.patch
Patch59: cirrus-Use-latest-stable-FreeBSD-images.patch
Patch60: cirrus-Use-FreeBSD-12.1-stable-release.patch
Patch61: rhel-Support-RHEL-7.8-kernel-module-rpm-build.patch
Patch62: dpif-netdev-Avoid-infinite-re-addition-of-misconfigu.patch
Patch63: netdev-afxdp-Avoid-removing-of-XDP-program-if-not-lo.patch
Patch64: system-afxdp.at-Add-test-for-infinite-re-addition-of.patch
Patch65: ovsdb-cluster.at-Wait-until-leader-is-elected-before.patch
Patch66: ovsdb-raft-Fix-the-problem-when-cluster-restarted-af.patch
Patch67: Modify-the-referenced-header-file.patch

#Source1: openvswitch-init
Buildroot: /tmp/openvswitch-xen-rpm
Provides: kmod-openvswitch
Conflicts: kmod-openvswitch

BuildRequires: python-six
BuildRequires: openssl-devel
BuildRequires: checkpolicy, selinux-policy-devel
BuildRequires: autoconf, automake, libtool
BuildRequires: python-sphinx
BuildRequires:  kernel kernel-devel
%undefine _enable_debug_packages
%description
Open vSwitch Linux kernel module

%prep
%setup -q -n openvswitch-%{version}
%autopatch -p1

%build
sh boot.sh
for kv in %{kversion}; do
    mkdir -p _$kv
    (cd _$kv && /bin/cp -f ../configure . && %configure --srcdir=.. \
        --with-linux=/lib/modules/${kv}/build --enable-ssl %{_ovs_config_extra_flags})
    make %{_smp_mflags} -C _$kv/datapath/linux
done

%install
export INSTALL_MOD_DIR=extra/openvswitch
rm -rf $RPM_BUILD_ROOT
for kv in %{kversion}; do
    make INSTALL_MOD_PATH=$RPM_BUILD_ROOT -C _$kv/datapath/linux modules_install
done
mkdir -p $RPM_BUILD_ROOT/etc/depmod.d
for kv in %{kversion}; do
    for module in $RPM_BUILD_ROOT/lib/modules/${kv}/extra/openvswitch/*.ko
    do
        modname="$(basename ${module})"
        grep -qsPo "^\s*override ${modname%.ko} \* extra\/openvwitch" \
            $RPM_BUILD_ROOT/etc/depmod.d/kmod-openvswitch.conf || \
            echo "override ${modname%.ko} * extra/openvswitch" >> \
            $RPM_BUILD_ROOT/etc/depmod.d/kmod-openvswitch.conf
        grep -qsPo "^\s*override ${modname%.ko} \* weak-updates\/openvwitch" \
            $RPM_BUILD_ROOT/etc/depmod.d/kmod-openvswitch.conf || \
            echo "override ${modname%.ko} * weak-updates/openvswitch" >> \
            $RPM_BUILD_ROOT/etc/depmod.d/kmod-openvswitch.conf
    done
done
install -d -m 0755 $RPM_BUILD_ROOT/usr/share/openvswitch/scripts
install -p -m 0755 rhel/usr_share_openvswitch_scripts_ovs-kmod-manage.sh \
    $RPM_BUILD_ROOT/usr/share/openvswitch/scripts/ovs-kmod-manage.sh

%clean
rm -rf $RPM_BUILD_ROOT

%post
current_kernel=$(uname -r)
IFS=. read installed_major installed_minor installed_micro installed_arch \
    installed_build <<<"${current_kernel##*-}"
if [ "$installed_major" = "327" ] || [ "$installed_major" = "693" ]; then
    # Workaround for RHEL 7.2 and 7.4
    if [ -x "/usr/share/%{oname}/scripts/ovs-kmod-manage.sh" ]; then
        /usr/share/%{oname}/scripts/ovs-kmod-manage.sh
    fi
else
    # Ensure that modprobe will find our modules.
    for k in $(cd /lib/modules && /bin/ls); do
        [ -d "/lib/modules/$k/kernel/" ] && /sbin/depmod -a "$k"
    done
    if [ -x "/sbin/weak-modules" ]; then
        for m in openvswitch vport-gre vport-stt vport-geneve \
                 vport-lisp vport-vxlan; do
            echo "/lib/modules/%{kernel}/extra/openvswitch/$m.ko"
        done | /sbin/weak-modules --add-modules
    fi
fi

%postun
if [ "$1" = 0 ]; then  # Erase, not upgrade
    for kname in `ls -d /lib/modules/*`
    do
        rm -rf $kname/weak-updates/openvswitch
    done
fi
/sbin/depmod -a

%files
%defattr(0644,root,root)
/lib/modules/*/extra/openvswitch/*.ko
%exclude /lib/modules/*/modules.*
/etc/depmod.d/kmod-openvswitch.conf
%attr(755,root,root) /usr/share/openvswitch/scripts/ovs-kmod-manage.sh

%changelog
* Tue Sep 01 2020 zhangjiapeng <zhangjiapeng9@huawei.com> - 2.12.0
- Modify the referenced header file

* Sat Dec 21 2019 openEuler Buildteam <buildteam@openeuler.org> - 2.12.0
- Add opensource patch 

* Fri Nov 22 2019 openEuler Buildteam <buildteam@openeuler.org> - 2.12.0
- First build 
