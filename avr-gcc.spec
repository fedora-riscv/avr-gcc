%define target avr

Name:           %{target}-gcc
Version:        4.5.1
Release:        1%{?dist}
Summary:        Cross Compiling GNU GCC targeted at %{target}
Group:          Development/Languages
License:        GPLv2+
URL:            http://gcc.gnu.org/
Source0:        ftp://ftp.gnu.org/gnu/gcc/gcc-%{version}/gcc-core-%{version}.tar.bz2
Source1:        ftp://ftp.gnu.org/gnu/gcc/gcc-%{version}/gcc-g++-%{version}.tar.bz2
Source2:        README.fedora
Patch0:         avr-gcc-4.5.0-new_devices.patch

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-%(%{__id_u} -n)
BuildRequires:  %{target}-binutils >= 2.13, zlib-devel gawk gmp-devel mpfr-devel libmpc-devel
Requires:       %{target}-binutils >= 2.13

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
%setup -q -c -a 1
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
  sed -e 's,find $RPM_BUILD_ROOT,find $RPM_BUILD_ROOT%_bindir $RPM_BUILD_ROOT%_libexecdir,' $a > $b
  chmod a+x $b
  ;;
esac
done

sed -e 's,^[ ]*/usr/lib/rpm.*/brp-strip,./brp-strip,' \
< os_install_post~ > os_install_post 


%build
mkdir -p gcc-%{target}
pushd gcc-%{target}
CC="%{__cc} ${RPM_OPT_FLAGS}" \
../gcc-%{version}/configure --prefix=%{_prefix} --mandir=%{_mandir} \
  --infodir=%{_infodir} --target=%{target} --enable-languages=c,c++ \
  --disable-nls --disable-libssp --with-system-zlib \
  --enable-version-specific-runtime-libs \
  --with-pkgversion="Fedora %{version}-%{release}" \
  --with-bugurl="https://bugzilla.redhat.com/"
# In general, building GCC is not smp-safe
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
rm    $RPM_BUILD_ROOT%{_libdir}/libiberty.a
# and these aren't usefull for embedded targets
rm -r $RPM_BUILD_ROOT/usr/lib/gcc/%{target}/%{version}/install-tools
rm -r $RPM_BUILD_ROOT%{_libexecdir}/gcc/%{target}/%{version}/install-tools

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

* Thu Apr 20 2007 Koos Termeulen <koostermeulen@gmail.com> 4.1.2-1
- Initial release
