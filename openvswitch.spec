%bcond_with dpdk

%ifarch x86_64
%bcond_without check
%else
%bcond_with check
%endif

%bcond_with check_datapath_kernel
%bcond_without libcapng

Name: openvswitch
Summary: Open vSwitch daemon/database/utilities
URL: https://www.openvswitch.org/
Version: 2.17.5
Release: 1
License: ASL 2.0 and LGPLv2+ and SISSL

Source0: https://www.openvswitch.org/releases/%{name}-%{version}.tar.gz
Source1: openvswitch.sysusers

Patch0000:      0000-openvswitch-add-stack-protector-strong.patch
Patch0002:      0002-Remove-unsupported-permission-names.patch
Patch0003:      fix-selinux-err.patch

BuildRequires: gcc gcc-c++ make
BuildRequires: autoconf automake libtool
BuildRequires: openssl openssl-devel
BuildRequires: python3-devel python3-six python3-setuptools
BuildRequires: python3-sphinx
BuildRequires: desktop-file-utils
BuildRequires: groff-base graphviz
BuildRequires: unbound-devel
# make check dependencies
BuildRequires: procps-ng

%if %{with check_datapath_kernel}
BuildRequires: nmap-ncat
%endif
 
%if %{with libcapng}
BuildRequires: libcap-ng libcap-ng-devel
%endif
 
%if %{with dpdk}
BuildRequires: dpdk-devel libpcap-devel numactl-devel
%endif

Requires: openssl iproute module-init-tools

%{?systemd_requires}
%{?sysusers_requires_compat}

Requires(post): /bin/sed
Requires(post): %{_sbindir}/update-alternatives
Requires(postun): %{_sbindir}/update-alternatives
Obsoletes: openvswitch-controller <= 0:2.1.0-1

%description
Open vSwitch provides standard network bridging functions and
support for the OpenFlow protocol for remote per-flow control of
traffic.

%package -n python3-openvswitch
Summary: Open vSwitch python3 bindings
License: ASL 2.0
Requires: python3 python3-six
Obsoletes: python-openvswitch < 2.10.0-6
Provides: python-openvswitch = %{version}-%{release}

%description -n python3-openvswitch
Python bindings for the Open vSwitch database

%package test
Summary: Open vSwitch testing utilities
License: ASL 2.0
BuildArch: noarch
Requires: python3-openvswitch = %{version}-%{release}

%description test
Utilities that are useful to diagnose performance and connectivity
issues in Open vSwitch setup.

%package testcontroller
Summary: Simple controller for testing OpenFlow setups
License: ASL 2.0
Requires: openvswitch = %{version}-%{release}

%description testcontroller
This controller enables OpenFlow switches that connect to it to act as
MAC-learning Ethernet switches.
It can be used for initial testing of OpenFlow networks.
It is not a necessary or desirable part of a production OpenFlow deployment.

%package devel
Summary: Open vSwitch OpenFlow development package (library, headers)
License: ASL 2.0

%description devel
This provides shared library, libopenswitch.so and the openvswitch header
files needed to build an external application.

%package -n network-scripts-%{name}
Summary: Open vSwitch legacy network service support
License: ASL 2.0
Requires: network-scripts
Supplements: (%{name} and network-scripts)
 
%description -n network-scripts-%{name}
This provides the ifup and ifdown scripts for use with the legacy network
service.
%package ipsec
Summary: Open vSwitch IPsec tunneling support
License: ASL 2.0
Requires: openvswitch libreswan
Requires: python3-openvswitch = %{version}-%{release}

%description ipsec
This package provides IPsec tunneling support for OVS tunnels.

%if %{with dpdk}
%package dpdk
Summary: Open vSwitch OpenFlow development package (switch, linked with DPDK)
License: ASL 2.0
Supplements: %{name}

%description dpdk
This provides ovs-vswitchd linked with DPDK library.
%endif

%prep
%autosetup -p 1
export PKG_CONFIG_PATH=/usr/lib64/pkgconfig

%build
rm -f python/ovs/dirs.py
autoreconf

./boot.sh
mkdir build build-dpdk
pushd build
ln -s ../configure
%configure \
        --disable-libcapng \
        --disable-static \
        --enable-shared \
        --enable-ssl \
        --with-pkidir=%{_sharedstatedir}/openvswitch/pki
make %{?_smp_mflags}
popd
%if %{with dpdk}
pushd build-dpdk
ln -s ../configure
%configure \
        --disable-libcapng \
        --disable-static \
        --enable-shared \
        --enable-ssl \
        --with-dpdk=shared \
        --with-pkidir=%{_sharedstatedir}/openvswitch/pki \
        --libdir=%{_libdir}/openvswitch-dpdk \
        --program-suffix=.dpdk
make %{?_smp_mflags}
popd
%endif
/usr/bin/python3 build-aux/dpdkstrip.py \
        --dpdk \
        < rhel/usr_lib_systemd_system_ovs-vswitchd.service.in \
        > rhel/usr_lib_systemd_system_ovs-vswitchd.service


%install
rm -rf $RPM_BUILD_ROOT

%if %{with dpdk}
make -C build-dpdk install-exec DESTDIR=$RPM_BUILD_ROOT

# We only need ovs-vswitchd-dpdk and some libraries for dpdk subpackage
rm -rf $RPM_BUILD_ROOT%{_bindir}
find $RPM_BUILD_ROOT%{_sbindir} -mindepth 1 -maxdepth 1 -not -name ovs-vswitchd.dpdk -delete
find $RPM_BUILD_ROOT%{_libdir}/openvswitch-dpdk -mindepth 1 -maxdepth 1 -not -name "libofproto*.so.*" -not -name "libopenvswitch*.so.*" -delete
%endif

make -C build install DESTDIR=$RPM_BUILD_ROOT
mv $RPM_BUILD_ROOT%{_sbindir}/ovs-vswitchd $RPM_BUILD_ROOT%{_sbindir}/ovs-vswitchd.nodpdk
touch $RPM_BUILD_ROOT%{_sbindir}/ovs-vswitchd

install -d -m 0755 $RPM_BUILD_ROOT/run/openvswitch
install -d -m 0750 $RPM_BUILD_ROOT%{_localstatedir}/log/openvswitch
install -d -m 0755 $RPM_BUILD_ROOT%{_sysconfdir}/openvswitch

install -p -D -m 0644 %{SOURCE1} $RPM_BUILD_ROOT%{_sysusersdir}/openvswitch.conf

install -p -D -m 0644 rhel/usr_lib_udev_rules.d_91-vfio.rules \
        $RPM_BUILD_ROOT%{_udevrulesdir}/91-vfio.rules

install -p -D -m 0644 \
        rhel/usr_share_openvswitch_scripts_systemd_sysconfig.template \
        $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/openvswitch

for service in openvswitch ovsdb-server ovs-vswitchd ovs-delete-transient-ports \
               openvswitch-ipsec; do
        install -p -D -m 0644 \
                        rhel/usr_lib_systemd_system_${service}.service \
                        $RPM_BUILD_ROOT%{_unitdir}/${service}.service
done

install -m 0755 rhel/etc_init.d_openvswitch \
        $RPM_BUILD_ROOT%{_datadir}/openvswitch/scripts/openvswitch.init

install -p -D -m 0644 rhel/etc_openvswitch_default.conf \
        $RPM_BUILD_ROOT/%{_sysconfdir}/openvswitch/default.conf

install -p -D -m 0644 rhel/etc_logrotate.d_openvswitch \
        $RPM_BUILD_ROOT/%{_sysconfdir}/logrotate.d/openvswitch

install -m 0644 vswitchd/vswitch.ovsschema \
        $RPM_BUILD_ROOT/%{_datadir}/openvswitch/vswitch.ovsschema

install -d -m 0755 $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/network-scripts/
install -p -m 0755 rhel/etc_sysconfig_network-scripts_ifdown-ovs \
        $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/network-scripts/ifdown-ovs
install -p -m 0755 rhel/etc_sysconfig_network-scripts_ifup-ovs \
        $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/network-scripts/ifup-ovs
 
install -d -m 0755 $RPM_BUILD_ROOT%{python3_sitelib}
cp -a $RPM_BUILD_ROOT/%{_datadir}/openvswitch/python/ovstest \
        $RPM_BUILD_ROOT%{python3_sitelib}

# Build the JSON C extension for the Python lib (#1417738)
pushd python
(
export CPPFLAGS="-I ../include"
export LDFLAGS="%{__global_ldflags} -L $RPM_BUILD_ROOT%{_libdir}"
%py3_build
%py3_install
[ -f "$RPM_BUILD_ROOT/%{python3_sitearch}/ovs/_json$(python3-config --extension-suffix)" ]
)
popd

rm -rf $RPM_BUILD_ROOT/%{_datadir}/openvswitch/python/

install -d -m 0755 $RPM_BUILD_ROOT/%{_sharedstatedir}/openvswitch

install -d -m 0755 $RPM_BUILD_ROOT%{_prefix}/lib/firewalld/services/

install -p -D -m 0755 \
        rhel/usr_share_openvswitch_scripts_ovs-systemd-reload \
        $RPM_BUILD_ROOT%{_datadir}/openvswitch/scripts/ovs-systemd-reload

touch $RPM_BUILD_ROOT%{_sysconfdir}/openvswitch/conf.db
touch $RPM_BUILD_ROOT%{_sysconfdir}/openvswitch/system-id.conf

# remove unpackaged files
rm -f $RPM_BUILD_ROOT/%{_bindir}/ovs-benchmark \
        $RPM_BUILD_ROOT/%{_bindir}/ovs-docker \
        $RPM_BUILD_ROOT/%{_bindir}/ovs-parse-backtrace \
        $RPM_BUILD_ROOT/%{_sbindir}/ovs-vlan-bug-workaround

rm -rf $RPM_BUILD_ROOT/%{_mandir}/*

# remove ovn unpackages files
rm -f $RPM_BUILD_ROOT%{_bindir}/ovn*
rm -f $RPM_BUILD_ROOT%{_datadir}/openvswitch/ovn*
rm -f $RPM_BUILD_ROOT%{_datadir}/openvswitch/scripts/ovn*
rm -f $RPM_BUILD_ROOT%{_includedir}/ovn/*

%check
for dir in build \
%if %{with dpdk}
%ifarch %{dpdkarches}
build-dpdk \
%endif
%endif
; do
pushd $dir
%if %{with check}
    touch resolv.conf
    export OVS_RESOLV_CONF=$(pwd)/resolv.conf
    if make check TESTSUITEFLAGS='%{_smp_mflags}' ||
       make check TESTSUITEFLAGS='--recheck' ||
       make check TESTSUITEFLAGS='--recheck'; then :;
    else
        cat tests/testsuite.log
        exit 1
    fi
%endif
%if %{with check_datapath_kernel}
    if make check-kernel RECHECK=yes; then :;
    else
        cat tests/system-kmod-testsuite.log
        exit 1
    fi
%endif
popd
done
 
%preun
%if 0%{?systemd_preun:1}
    %systemd_preun %{name}.service
%else
    if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
        /bin/systemctl --no-reload disable %{name}.service >/dev/null 2>&1 || :
        /bin/systemctl stop %{name}.service >/dev/null 2>&1 || :
    fi
%endif

%pre

%post
%{_sbindir}/update-alternatives --install %{_sbindir}/ovs-vswitchd \
  ovs-vswitchd %{_sbindir}/ovs-vswitchd.nodpdk 10
if [ $1 -eq 1 ]; then
    sed -i 's:^#OVS_USER_ID=:OVS_USER_ID=:' /etc/sysconfig/openvswitch

    sed -i \
        's@OVS_USER_ID="openvswitch:openvswitch"@OVS_USER_ID="openvswitch:hugetlbfs"@'\
        /etc/sysconfig/openvswitch
fi
chown -R openvswitch:openvswitch /etc/openvswitch

%if 0%{?systemd_post:1}
    %systemd_post %{name}.service
%else
    # Package install, not upgrade
    if [ $1 -eq 1 ]; then
        /bin/systemctl daemon-reload >dev/null || :
    fi
%endif

%postun
if [ $1 -eq 0 ] ; then
  %{_sbindir}/update-alternatives --remove ovs-vswitchd %{_sbindir}/ovs-vswitchd.nodpdk
fi
%if 0%{?systemd_postun:1}
    %systemd_postun %{name}.service
%else
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
%endif

%if %{with dpdk}
%post dpdk
if fgrep -qw sse4_1 /proc/cpuinfo; then
    priority=20
else
    echo "Warning: the CPU doesn't support SSE 4.1, dpdk support is not enabled." >&2
    priority=5
fi
%{_sbindir}/update-alternatives --install %{_sbindir}/ovs-vswitchd \
  ovs-vswitchd %{_sbindir}/ovs-vswitchd.dpdk $priority

%postun dpdk
if [ $1 -eq 0 ] ; then
  %{_sbindir}/update-alternatives --remove ovs-vswitchd %{_sbindir}/ovs-vswitchd.dpdk
fi
%endif

%files -n python3-openvswitch
%{python3_sitearch}/ovs
%{python3_sitearch}/ovs-*.egg-info
%{_datadir}/openvswitch/bugtool-plugins/
%{_datadir}/openvswitch/scripts/ovs-bugtool-*
%{_datadir}/openvswitch/scripts/ovs-check-dead-ifs
%{_datadir}/openvswitch/scripts/ovs-vtep
%{_bindir}/ovs-dpctl-top
%{_sbindir}/ovs-bugtool
%doc LICENSE

%files test
%{_bindir}/ovs-pcap
%{_bindir}/ovs-tcpdump
%{_bindir}/ovs-tcpundump
%{_bindir}/ovs-test
%{_bindir}/ovs-vlan-test
%{_bindir}/ovs-l3ping
%{python3_sitelib}/ovstest

%files testcontroller
%{_bindir}/ovs-testcontroller

%files devel
%{_libdir}/*.so
%{_libdir}/pkgconfig/*.pc
%{_includedir}/openvswitch/*
%{_includedir}/openflow/*
%exclude %{_libdir}/*.a
%exclude %{_libdir}/*.la

%files -n network-scripts-%{name}
%{_sysconfdir}/sysconfig/network-scripts/ifup-ovs
%{_sysconfdir}/sysconfig/network-scripts/ifdown-ovs
%files ipsec
%{_datadir}/openvswitch/scripts/ovs-monitor-ipsec
%{_unitdir}/openvswitch-ipsec.service

%if %{with dpdk}
%files dpdk
%{_libdir}/openvswitch-dpdk/
%ghost %{_sbindir}/ovs-vswitchd
%{_sbindir}/ovs-vswitchd.dpdk
%endif

%files
%defattr(-,openvswitch,openvswitch)
%dir %{_sysconfdir}/openvswitch
%{_sysconfdir}/openvswitch/default.conf
%config %ghost %verify(not owner group md5 size mtime) %{_sysconfdir}/openvswitch/conf.db
%ghost %attr(0600,-,-) %verify(not owner group md5 size mtime) %{_sysconfdir}/openvswitch/.conf.db.~lock~
%config %ghost %{_sysconfdir}/openvswitch/system-id.conf
%defattr(-,root,root)
%config(noreplace) %verify(not md5 size mtime) %{_sysconfdir}/sysconfig/openvswitch
%{_sysconfdir}/bash_completion.d/ovs-appctl-bashcomp.bash
%{_sysconfdir}/bash_completion.d/ovs-vsctl-bashcomp.bash
%config(noreplace) %{_sysconfdir}/logrotate.d/openvswitch
%{_unitdir}/openvswitch.service
%{_unitdir}/ovsdb-server.service
%{_unitdir}/ovs-vswitchd.service
%{_unitdir}/ovs-delete-transient-ports.service
%{_datadir}/openvswitch/scripts/openvswitch.init
%{_datadir}/openvswitch/scripts/ovs-lib
%{_datadir}/openvswitch/scripts/ovs-save
%{_datadir}/openvswitch/scripts/ovs-ctl
%{_datadir}/openvswitch/scripts/ovs-kmod-ctl
%{_datadir}/openvswitch/scripts/ovs-systemd-reload
%config %{_datadir}/openvswitch/local-config.ovsschema
%config %{_datadir}/openvswitch/vswitch.ovsschema
%config %{_datadir}/openvswitch/vtep.ovsschema
%{_bindir}/ovs-appctl
%{_bindir}/ovs-dpctl
%{_bindir}/ovs-ofctl
%{_bindir}/ovs-vsctl
%{_bindir}/ovsdb-client
%{_bindir}/ovsdb-tool
%{_bindir}/ovs-pki
%{_bindir}/vtep-ctl
%{_libdir}/*.so.*
%ghost %{_sbindir}/ovs-vswitchd
%{_sbindir}/ovs-vswitchd.nodpdk
%{_sbindir}/ovsdb-server
%{_udevrulesdir}/91-vfio.rules
%doc LICENSE NOTICE README.rst NEWS rhel/README.RHEL.rst
/var/lib/openvswitch
%attr(750,openvswitch,openvswitch) %verify(not owner group) /var/log/openvswitch
%ghost %attr(755,root,root) %verify(not owner group) /run/openvswitch
%{_sysconfdir}/sysconfig/network-scripts/ifup-ovs
%{_sysconfdir}/sysconfig/network-scripts/ifdown-ovs
%{_sysusersdir}/openvswitch.conf

%changelog
* Tue Jan 03 2023 wanglimin <wanglimin@xfusion.com> - 2.17.5-1
- upgrade to 2.17.5-1

* Thu Dec 29 2022 zhouwenpei <zhouwenpei1@h-pattners.com> - 2.12.4-2
- fix CVE-2022-4338

* Wed Sep 28 2022 zhouwenpei <zhouwenpei1@h-pattners.com> - 2.12.4-1
- upgrade to 2.12.4

* Mon Jul 25 2022 zhouwenpei <zhouwenpei1@h-pattners.com> - 2.12.0-22
- revent "Add ovn-central ovn-central and ovn-host subpackage"

* Wed Jul 13 2022 zhouwenpei <zhouwenpei1@h-pattners.com> - 2.12.0-21
- fix CVE-2021-3905

* Wed May 18 2022 jiangxinyu <jiangxinyu@kylinos.cn> - 2.12.0-20
- Add ovn-central ovn-central and ovn-host subpackage

* Thu Sep 2 2021 hanhui <hanhui15@huawei.com> - 2.12.0-19
- Fix selinux preventing ovs-kmod-ctl err

* Wed Sep 1 2021 hanhui <hanhui15@huawei.com> - 2.12.0-18
- Change the OVS startup mode to service startup.

* Tue Aug 3 2021 huangtianhua <huangtianhua@huawei.com> - 2.12.0-17
- Adds python3-ovs as provide

* Thu Jul 29 2021 liuyumeng <liuyumeng5@huawei.com> - 2.12.0-16
- Type:cve
- ID:CVE-2021-36980 
- SUG:NA
- DESC: fix CVE-2021-36980

* Tue Mar 30 2021 wangyue <wangyue92@huawei.com> - 2.12.0-15
- fix CVE-2020-27827 and CVE-2015-8011

* Mon Mar 01 2021 wangyue <wangyue92@huawei.com> - 2.12.0-14
- fix CVE-2020-35498

* Sun Feb 07 2021 luosuwang <oenetdev@huawei.com> - 2.12.0-13
- Add python3.Xdist(ovs)

* Thu Jan 21 2021 luosuwang <oenetdev@huawei.com> - 2.12.0-12
- Remove build_python3 option to complie python3-openvswitch package by default

* Tue Jan 05 2021 luosuwang <oenetdev@huawei.com> - 2.12.0-11
- Add the option of compiling python3-openvswitch package

* Thu Sep 24 2020 luosuwang <oenetdev@huawei.com> - 2.12.0-10
- Fix ovs-tcpdump import error

* Tue Sep 22 2020 luosuwang <oenetdev@huawei.com> - 2.12.0-9
- Remove openvswitch-kmod package

* Wed Sep 09 2020 zhangjiapeng <zhangjiapeng9@huawei.com> - 2.12.0-8
- Remove unsupported permission names

* Tue Sep 01 2020 zhangjiapeng <zhangjiapeng9@huawei.com> - 2.12.0-7
- Add openvswitch-kmod package

* Thu Aug 20 2020 zhangjiapeng <zhangjiapeng9@huawei.com> - 2.12.0-6
- Change the dependent python package from python2 to python3

* Wed Mar 18 2020 zhangtao <zhangtao221@huawei.com> - 2.12.0-5
- add stack protector

* Tue Mar 17 2020 gulining <gulining1@huawei.com> - 2.12.0-4
- remove extra spaces to resolve compile error

* Mon Mar 16 2020 jiangkai <jiangkai20@huawei.com> - 2.12.0-3
- Package init
