%define target avr

Name:           %{target}-gcc
Version:        5.2.0
Release:        1%{?dist}
Summary:        Cross Compiling GNU GCC targeted at %{target}
Group:          Development/Languages
License:        GPLv2+
URL:            http://gcc.gnu.org/
Source0:        ftp://ftp.gnu.org/gnu/gcc/gcc-%{version}/gcc-%{version}.tar.bz2
Source2:        README.fedora

Patch0:         avr-gcc-4.5.3-mint8.patch

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-%(%{__id_u} -n)
BuildRequires:  %{target}-binutils >= 1:2.23, zlib-devel gawk gmp-devel mpfr-devel libmpc-devel, flex
#for autoreconf:
BuildRequires:  gettext-devel autoconf automake
Requires:       %{target}-binutils >= 1:2.23
Provides:       bundled(libiberty)

%description
This is a Cross Compiling version of GNU GCC, which can be used to
compile for the %{target} platform, instead of for the
native %{_arch} platform.


%package c++
Summary:        Cross Compiling GNU GCC targeted at %{target}
Group:          Development/Languages
Requires:       %{name} = %{version}-%{release}

%description c++
This package contains the Cross Compiling version of g++, which can be used to
compile c++ code for the %{target} platform, instead of for the native %{_arch}
platform.


%prep
%setup -q -c
[ -d gcc-%{version} ] || mv gcc-4.7-* gcc-%{version}

pushd gcc-%{version}
%patch0 -p0

contrib/gcc_update --touch
popd
cp -a %{SOURCE2} .

# Extract %%__os_install_post into os_install_post~
cat << \EOF > os_install_post~
%__os_install_post
EOF

# Generate customized brp-*scripts
cat os_install_post~ | while read a x y; do
case $a in
# Prevent brp-strip* from trying to handle foreign binaries
*/brp-strip*)
  b=$(basename $a)
  sed -e 's,find "*$RPM_BUILD_ROOT"*,find "$RPM_BUILD_ROOT%_bindir" "$RPM_BUILD_ROOT%_libexecdir",' $a > $b
  chmod a+x $b
  ;;
esac
done

sed -e 's,^[ ]*/usr/lib/rpm.*/brp-strip,./brp-strip,' \
< os_install_post~ > os_install_post 


%build
pushd gcc-%{version}
acv=$(autoreconf --version | head -n1)
acv=${acv##* }
sed -i "/_GCC_AUTOCONF_VERSION/s/2.64/$acv/" config/override.m4
autoreconf -fiv
popd
mkdir -p gcc-%{target}
pushd gcc-%{target}
CC="%{__cc} ${RPM_OPT_FLAGS} -fno-stack-protector" \
../gcc-%{version}/configure --prefix=%{_prefix} --mandir=%{_mandir} \
  --infodir=%{_infodir} --target=%{target} --enable-languages=c,c++ \
  --disable-nls --disable-libssp --with-system-zlib \
  --enable-version-specific-runtime-libs \
  --with-pkgversion="Fedora %{version}-%{release}" \
  --with-bugurl="https://bugzilla.redhat.com/"
make
popd


%install
rm -rf $RPM_BUILD_ROOT
pushd gcc-%{target}
make install DESTDIR=$RPM_BUILD_ROOT
popd
# we don't want these as we are a cross version
rm -r $RPM_BUILD_ROOT%{_infodir}
rm -r $RPM_BUILD_ROOT%{_mandir}/man7
rm    $RPM_BUILD_ROOT%{_libdir}/libiberty.a ||:
rm    $RPM_BUILD_ROOT%{_libdir}/libcc1* ||:
# and these aren't usefull for embedded targets
rm -r $RPM_BUILD_ROOT/usr/lib/gcc/%{target}/%{version}/install-tools ||:
rm -r $RPM_BUILD_ROOT%{_libexecdir}/gcc/%{target}/%{version}/install-tools ||:

%define __os_install_post . ./os_install_post


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc gcc-%{version}/COPYING gcc-%{version}/COPYING.LIB
%doc gcc-%{version}/README README.fedora
%{_bindir}/%{target}-*
%dir /usr/lib/gcc
%dir /usr/lib/gcc/%{target}
/usr/lib/gcc/%{target}/%{version}
%dir %{_libexecdir}/gcc
%dir %{_libexecdir}/gcc/%{target}
%{_libexecdir}/gcc/%{target}/%{version}
%{_mandir}/man1/%{target}-*.1.gz
%exclude %{_bindir}/%{target}-?++
%exclude %{_libexecdir}/gcc/%{target}/%{version}/cc1plus
%exclude %{_mandir}/man1/%{target}-g++.1.gz

%files c++
%defattr(-,root,root,-)
%{_bindir}/%{target}-?++
%{_libexecdir}/gcc/%{target}/%{version}/cc1plus
%{_mandir}/man1/%{target}-g++.1.gz


%changelog
* Wed Sep 02 2015 Michal Hlavinka <mhlavink@redhat.com> - 5.2.0-1
- updated to 5.2.0

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.1.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon May 25 2015 Michal Hlavinka <mhlavink@redhat.com> - 5.1.0-1
- updated to 5.1.0

* Sat May 02 2015 Kalev Lember <kalevlember@gmail.com> - 4.9.2-2
- Rebuilt for GCC 5 C++11 ABI change

* Thu Oct 30 2014 Michal Hlavinka <mhlavink@redhat.com> - 4.9.2-1
- updated to 4.9.2

* Fri Aug 29 2014 Michal Hlavinka <mhlavink@redhat.com> - 4.9.1-3
- update workaround that prevents stripping of avr libraries (#1134394)

* Fri Aug 15 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.9.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Wed Aug 13 2014 Michal Hlavinka <mhlavink@redhat.com> - 4.9.1-1
- updated to 4.9.1

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.9.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue Apr 29 2014 Michal Hlavinka <mhlavink@redhat.com> - 4.9.0-1
- updated to 4.9.0

* Wed Mar 05 2014 Michal Hlavinka <mhlavink@redhat.com> - 4.8.2-2
- silent false positive warnings about misspelled __vector_NN

* Wed Oct 16 2013 Michal Hlavinka <mhlavink@redhat.com> - 4.8.2-1
- updated to 4.8.2

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.8.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon Jun 24 2013 Michal Hlavinka <mhlavink@redhat.com> - 4.8.1-1
- updated to 4.8.1

* Wed Jun 12 2013 Michal Hlavinka <mhlavink@redhat.com> - 4.7.3-2
- rebuilt with real 4.7.3 sources

* Fri Apr 19 2013 Michal Hlavinka <mhlavink@redhat.com> - 4.7.3-1
- fix aarch64 support (#925063)

* Fri Feb 22 2013 Michal Hlavinka <mhlavink@redhat.com> - 4.7.3-0.1
- fix FTBS: incompatible changes in TeX
- updated to 4.7.3 pre-release

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.7.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Nov 15 2012 Michal Hlavinka <mhlavink@redhat.com> - 4.7.2-1
- updated to 4.7.2

* Mon Oct 15 2012 Jon Ciesla <limburgher@gmail.com> - 4.6.3-3
- Provides: bundled(libiberty)

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.6.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Mar  5 2012 Tom Callaway <spot@fedoraproject.org> - 4.6.3-1
- update to 4.6.3

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.6.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Sun Dec 11 2011  Thibault North <tnorth@fedoraproject.org> - 4.6.2-1
- Update to 4.6.2
- Drop upstreamed patch

* Fri Nov 11 2011 Thibault North <tnorth@fedoraproject.org> - 4.6.1-4
- Rebuild with avr-binutils downgrade

* Thu Oct 20 2011 Marcela Mašláňová <mmaslano@redhat.com> - 4.6.1-3.1
- rebuild with new gmp without compat lib

* Sat Oct 15 2011 Thibault North <tnorth@fedoraproject.org> - 4.6.1-3
- Fix BZ#737950 thanks Jan Wildeboer

* Mon Oct 10 2011 Peter Schiffer <pschiffe@redhat.com> - 4.6.1-2.1
- rebuild with new gmp

* Wed Aug 31 2011 Thibault North <tnorth@fedoraproject.org> - 4.6.1-2
- Small cleanup

* Wed Aug 31 2011 Thibault North <tnorth@fedoraproject.org> - 4.6.1-1
- Updated to 4.6.1

* Sun May 1 2011 Thibault North <tnorth@fedoraproject.org> - 4.5.3-1
- Updated to 4.5.3
- Fix #626889

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.5.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Sep 29 2010 jkeating - 4.5.1-3
- Rebuilt for gcc bug 634757

* Fri Sep 24 2010 Thibault North <tnorth@fedoraproject.org> - 4.5.1-2
- Fix bug #637019 (gcc bug #45263) with the patch of Alastair D'Silva

* Tue Aug 3 2010 Thibault North <tnorth@fedoraproject.org> - 4.5.1-1
- Updated to 4.5.1

* Sun Jul 11 2010 Thibault North <tnorth@fedoraproject.org> - 4.5.0-2
- Add patch of Eric Weddington to support new devices and compile last avr-libc

* Fri Apr 16 2010 Thibault North <tnorth@fedoraproject.org> - 4.5.0-1
- New upstream release
- New build dependency: libmpc-devel
- Fix package version specification

* Fri Nov 20 2009 Thibault North <tnorth AT fedoraproject DOT org> - 4.4.2-1
- New upstream release

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.3.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.3.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Feb 14 2009 Thibault North <tnorth AT fedoraproject DOT org> - 4.3.3-1
- New upstream release: upgraded to 4.3.3
- Add dependencies to gmp-devel and mpfr-devel as build requires
- Remove patches (included upstream)

* Fri Oct 3 2008 Thibault North <tnorth AT fedoraproject DOT org> - 4.1.2-7
- Rebuild for gcc 4.3

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 4.1.2-6
- Autorebuild for GCC 4.3

* Fri Aug  3 2007 Hans de Goede <j.w.r.degoede@hhs.nl> 4.1.2-5
- Update License tag for new Licensing Guidelines compliance

* Sun May 20 2007 Hans de Goede <j.w.r.degoede@hhs.nl> 4.1.2-4
- Honor and use $RPM_OPT_FLAGS
- define VERSUFFIX to Fedora version-release, so that people can tell this is
  a patched / customized build
- Use gcc-core and gcc-g++ tarballs instead of the monolithic tarball
- Run contrib/gcc_update --touch after applying our patches
- In general, building GCC is not smp-safe, remove smpflags to play it safe
- Remove not usefull install-tools binaries
- Change %%{_libdir} into /usr/lib as gcc always installs its files under
  /usr/lib

* Mon May 14 2007 Hans de Goede <j.w.r.degoede@hhs.nl> 4.1.2-3
- Use normal make / make install instead off make all-gcc / make install-gcc
- Add --disable-libssp to the configure flags, freebsd ports, the avrlibc docs,
  and debian package all do this, and ./configure does not do this automaticly
- Add --enable-version-specific-runtime-libs, as we don't want gcc/g++ to be
  looking in the default include/lib paths
- Add --with-system-zlib and zlib-devel BR
- Add 2 usefull patches from freebsd ports collection
- Split g++ off into a seperate package
- Add special script/workaround to avoid debuginfo generation for non native
  libs

* Wed Apr 25 2007 Lennart Kneppers <lennartkneppers@gmail.com> 4.1.2-2
- Minor changes

* Fri Apr 20 2007 Koos Termeulen <koostermeulen@gmail.com> 4.1.2-1
- Initial release
