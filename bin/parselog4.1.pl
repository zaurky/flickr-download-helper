#!/usr/bin/perl
use strict;
use warnings;

use Term::ANSIColor;
#use Text::Reform;
use utf8;

my $now;
if (scalar @ARGV > 1) {
    $now = $ARGV[1];
} else {
    my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
    $now = sprintf "%04d-%02d-%02d", ($year+1900, $mon+1, $mday);
}

binmode STDOUT, ':utf8';

my $username = '';
my $date = '';
my $message = '';

#my $format = "| [[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[ | num = [[[[ (total ]]]]]), size = [[[[[[[[[[[[ (total ]]]]]]]]]]]]]) |";

my %h_id2username = ();
my %h_records = ();

open FILE, $ARGV[0];
binmode FILE, ':utf8';

while (<FILE>) {
    if (/WARNING username/) {
        chomp;
        my @a = split('WARNING', $_);
        $a[1] =~ s/.* = //;
        $username = $a[1];
        $date = $a[0];
    } elsif (/WARNING\s*(\d{6}):\s*username/) {
        my $id = $1;
        chomp;
        my @a = split('WARNING', $_);
        $a[1] =~ s/.* = //;
        $username = $a[1];
        $date = $a[0];
        $h_id2username{$id} = [$username, $date];
    } elsif (/(INFO|WARNING) download/) {
        chomp;
        s/.*(INFO|WARNING)//;
        my $num = 0;
        my $size = 0;
        if (/ download (\d+) file for (\d+) octets/) {
            $num = $1;
            $size = $2;
        }
        if ($username ne '' and !/ 0 /) {
            my @a_date = split(' ', $date);
            if (! defined $h_records{$username}) { $h_records{$username} = {}; }
            if (! defined $h_records{$username}{$a_date[0]}) { $h_records{$username}{$a_date[0]} = []; }
            push(@{$h_records{$username}{$a_date[0]}}, [$date, $username, $num, $size]);
        }
    } elsif (/(INFO|WARNING)\s*(\d{6}):\s*download/) {
        my $id = $2;
        chomp;
        s/.*(INFO|WARNING)\s*(\d{6}):\t//;
        if (defined $h_id2username{$id} and !/ 0 /) {
            my $num = 0;
            my $size = 0;
            if ($_ =~ /download (\d+) file for (\d+) octets/) {
                $num = $1;
                $size = $2;
            }

            my @a_date = split(' ', $h_id2username{$id}[1]);
            my $username = $h_id2username{$id}[0];
            if (! defined $h_records{$username}) { $h_records{$username} = {}; }
            if (! defined $h_records{$username}{$a_date[0]}) { $h_records{$username}{$a_date[0]} = []; }
            push(@{$h_records{$username}{$a_date[0]}}, [$h_id2username{$id}[1], $h_id2username{$id}[0], $num, $size]);
        }
    }
}
close FILE;

use Data::Dumper;

foreach $username (sort keys %h_records) {
    my $today;
    my $t_num = 0;
    my $t_size = 0;
    my $today_num = 0;
    my $today_size = 0;

    foreach $date (sort keys %{$h_records{$username}}) {
        if ($date eq $now) {
            my $daily = '';
            foreach $daily (@{$h_records{$username}{$date}}) {
                $today_num = $today_num + $daily->[2];
                $today_size = $today_size + $daily->[3];
            }
        } else {
            my $daily = '';
            foreach $daily (@{$h_records{$username}{$date}}) {
                $t_num = $t_num + $daily->[2];
                $t_size = $t_size + $daily->[3];
            }
        }
    }
    if ($t_num == 0) {
        print color "yellow";
    } elsif ($today_num != 0) {
        print color "red";
    }
    if ($today_num > 20) {
        print color "bold";
    }
    # "| [[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[ | num = [[[[ (total ]]]]]), size = [[[[[[[[[[[[ (total ]]]]]]]]]]]]]) |";
    # print form $format, $username, $today_num, ($t_num+$today_num), $today_size, ($t_size+$today_size);
    print "$username : $today_num (".($t_num+$today_num)."), $today_size (".($t_size+$today_size).")\n";
    print color "reset";
}

